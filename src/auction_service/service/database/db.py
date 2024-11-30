from pymongo import MongoClient
import json
import uuid
import random
import time
from bson import binary
unix_time = lambda: int(time.time())




class database:
    def __init__(self,auctionsFile,bidsFile):
        self.auctionsFile = auctionsFile
        self.bidsFile = bidsFile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "auctions" in self.db.list_collection_names():
            print(" \n\n DB ACTIVE  \n\n")
        else: 
            self.db_inizialization()


    def db_init_supp(self,collection,file):
        with open(file, "r") as file:
            data = json.load(file)
            if data:collection.insert_many(data)


    def db_inizialization(self):
        self.db.create_collection("auctions")
        auctions = self.db["auctions"]

        self.db.create_collection("bids")
        bids = self.db["bids"]

        self.db_init_supp(auctions,self.auctionsFile)
        self.db_init_supp(bids,self.bidsFile)



    ### SCHEDULED CHECK ###

    def checkAuctionExpiration(self):
        current_time = unix_time()  
        expired_auctions = []
        
        expired_auctions_cursor = self.db["auctions"].find({
            "end_time": {"$lt": current_time},
            "active": True
        })

        for auction in expired_auctions_cursor:

            expired_auctions.append(auction)
            self.db["auctions"].update_one({"auction_id": auction["auction_id"]}, {"$set": {"active": False}})

        return expired_auctions




    ### PLAYER ###
    
    def auction_create(self,player_id,gacha_id,starting_price,end_time):
        #control if gacha is already in bid
        #da fare con simo
        # if(not self.gacha_available(self,player_id,gacha_id)):return 1

        while(True):
            id=str(uuid.uuid4())
            if(not self.db["auctions"].find_one({"auction_id":id})):break
        
        auction={
            "auction_id":id,
            "player_id":player_id,"gacha_id":gacha_id,
            "starting_price":starting_price,
            "current_winning_player_id":None,
            "current_winning_bid":0,
            "end_time":end_time,
            "active":True
            }

        self.db["auctions"].insert_one(auction)
        return 0


    def auction_delete_player(self,player_id,auction_id,mock_distro):
        #return the bidded gacha
        if not mock_distro:
            pass

        return self.db["auctions"].delete_one({"player_id":player_id,"auction_id":auction_id})
        

    def auction_bid(self,auction_id,player_id,bid,mock_tux):
        auction = self.db["auctions"].find_one({"auction_id":auction_id,"active":True})
        if auction is None:return 1
        if player_id == auction["player_id"]: return 2
        if bid <= auction["current_winning_bid"]:return 3
        
        if not mock_tux:
            #restituire i soldi al player che stava vincendo 
            # e prendere quello che ha biddato
            pass
        
        auction["current_winning_player_id"]=player_id
        auction["current_winning_bid"]=bid

        self.db["bids"].insert_one({"player_id":player_id,"auction_id":auction_id,"bid":bid,"time":unix_time()})
        return 0

    def auction_active(self,player_id):
        return list(self.db["auctions"].find({"player_id":player_id,"active":True},{"_id":0}))


    def auction_active_all(self):
        return list(self.db["auctions"].find({"active":True},{"_id":0}))


    def auction_history_player(self,player_id):
        return list(self.db["auctions"].find({"player_id":player_id},{"_id":0}))


    def bid_history_player(self,player_id):
        return list(self.db["bids"].find({"player_id":player_id},{"_id":0}))


    def bid_history_player_auction(self,player_id,auction_id):
        return list(self.db["bids"].find({"player_id":player_id,"auction_id":auction_id},{"_id":0}))
    



    ######### ADMIN #########


    ##### AUCTION #####

    #auction_history same as player


    def auction_modify(self,auction_id,auction_modifier):
        #scoprire come rimuovere campi a None dal modifier
        self.db["auctions"].update_one({"auction_id":auction["auction_id"]},{"$set":auction})


    def auction_delete(self,auction_id,mock_distro):
        #return the bidded gacha
        if not mock_distro:
            pass

        return self.db["auctions"].delete_one({"auction_id":auction_id})
        


    def auction_info(self,auction_id):
            return self.db["auctions"].find_one({"auction_id":auction_id})
    
    
    def auction_history(self):
        return list(self.db["auctions"].find({},{"_id":0}))
    

    ##### BID #####

    #TODO bid_delete  (ricordarsi di fare il fallback sul bet minore),e tutto il resto

    def bid_create():
        #time less than ending
        #if finished amount must be lower
        #if ongoing amount cant be higher, if higher set winner to that, remove tux
        pass

    
    # BID_MODIFY
    def bid_modify(self,bid):
        #self.db["bid"].update_one({"auction_id":bid["auction_id"],"player_id":bid["player_id"]},{"$set":bid})


    # BID_DELETE
    def bid_delete(self,bid_id):
        return self.db["bids"].delete_one({"bid_id":bid["bid_id"]})
        
    
    def bid_history_auction(self,auction_id):
        return self.db["bids"].find({"auction_id":auction_id},{"_id":0})
    

    def bid_history(self):
        return self.db["bids"].find({},{"_id":0})
    

    # MARKET_ACTIVITY
    def market_activity(self):
        twenty_four_hours_ago = unix_time() - 86400
        auctions = self.db["bids"].find({"time": {"$gte": twenty_four_hours_ago}},{"_id":0})
        pipelineAvg = [
            {
                "$match": {
                    "time": {"$gte": twenty_four_hours_ago}  # Filter bids in the last 24 hours
                }
            },
            {
                "$group": {
                    "_id": None,  # No need to group by any field
                    "average_bid": {"$avg": "$bid"}  # Calculate the average of the 'bid' field
                }
            }
        ]
    
        pipelineCount = [
            {
                "$match": {
                    "time": {"$gte": twenty_four_hours_ago}  # Filter bids in the last 24 hours
                }
            },
            {
                "$count": "total_bids"  # Count the number of bids
            }
        ]
        
        # Perform aggregation for average bid and total bid count
        avg_result = self.db["bids"].aggregate(pipelineAvg)
        count_result = self.db["bids"].aggregate(pipelineCount)
        
        avg = list(avg_result) 
        count = list(count_result)  

        # Check if results are available
        avg_bid = avg[0]["average_bid"] if avg else 0
        total_bids = count[0]["total_bids"] if count else 0

        # Return the results
        return {"avg": avg_bid, "count": total_bids, "bids": auctions}




    #SUPPORT
    
    def auction_user_presence(self,player_id:str):
        return False if (self.db["auctions"].find_one({"player_id":player_id}) is None) else True 
    

    def auction_presence(self,auction_id:str):
        return False if (self.db["auctions"].find_one({"auction_id":auction_id}) is None) else True 

    def bid_user_presence(self,bid_id:str):
        return False if (self.db["bids"].find_one({"bid_id":bid_id}) is None) else True 
    
        






