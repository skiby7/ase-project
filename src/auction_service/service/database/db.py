from pymongo import MongoClient
import json
import uuid
import random
import time
unix_time = lambda: int(time.time())


#auctions and bids schemas
#both init together


#TODO user on db
class database:
    def __init__(self,auctionsFile,bidsFile):
        self.auctionsFile = auctionsFile
        self.bidsFile = bidsFile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "auctions" in self.db.list_collection_names():
            print(" \n\n DB ACTIVE  \n\n")
        else: 
            self.db_inizialization(self)
        
    # convert to json distro.txt
    def db_init_supp(collection,file):
        with open(file, "r") as file:
            data = json.load(file)
            collection.insert_many(data)

    def db_inizialization(self):
        self.db.create_collection("auctions")
        auctions = self.db["auctions"]

        self.db.create_collection("bids")
        bids = self.db["bids"]

        self.db_init_supp(auctions,self.auctionsFile)
        self.db_init_supp(bids,self.bidsFile)

    def checkAuctionExpiration(self):
        current_time = unix_time()  # Get the current Unix timestamp
        expired_auctions = []
        
        # Find all auctions where the end_time is less than the current time and the auction is still active
        expired_auctions_cursor = self.db["auctions"].find({
            "end_time": {"$lt": current_time},
            "active": True
        })

        # Iterate over the expired auctions and add them to the list
        for auction in expired_auctions_cursor:
            expired_auctions.append(auction)
            
            # Optional: You may want to deactivate the auction after it's expired
            self.db["auctions"].update_one({"auction_id": auction["auction_id"]}, {"$set": {"active": False}})

        return expired_auctions

    #PLAYER
    
    def auction_create(self,player_id,gacha_id,starting_price,end_time):
        #control if gacha is already in bid
        #da fare con simo
        # if(not self.gacha_available(self,player_id,gacha_id)):return 1

        while(True):
            id=uuid.uuid4()
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

    def auction_bid(self,auction_id,player_id,bid):
        auction = self.db["auctions"].find_one({"auction_id":id,"active":True})
        if auction is None:return 1
        if player_id == auction["player_id"]: return 2
        if bid <= auction["current_winning_bid"]:return 3

        auction["time"]=unix_time()
        auction["current_winning_player_id"]=player_id
        auction["current_winning_bid"]=bid

        self.db["bids"].insert_one({"player_id":player_id,"auction_id":auction_id,"bid":bid})
        return 0

    def auction_history(self,player_id):
        supp = list(self.db["auctions"].find({"player_id":player_id}))
        return [{"auction_id": auction["auction_id"],"player_id": auction["player_id"],"gacha_id": auction["auction_id"]} for auction in supp]
    

    #ADMIN
    #NB - because these are used by admins they contain _id
    def auction_history_player(self,player_id):
        return list(self.db["auctions"].find({"player_id":player_id}))


    def auction_info(self,auction_id):
        return self.db["auctions"].find_one({"auction_id":auction_id})
    
    def auction_modify(self,auction):
        self.db["auctions"].update_one({"player_id":auction["player_id"]},{"$set":auction})
    
    def auction_history_all(self):
        return list(self.db["auctions"].find())
    
    def market_activity(self):
        twenty_four_hours_ago = unix_time() - 86400
        auctions = self.db["bids"].find({"time": {"$gte": twenty_four_hours_ago}})
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
        
        # Extract the results from the aggregation cursors
        avg = list(avg_result)  # Convert to list to extract result
        count = list(count_result)  # Convert to list to extract result

        # Check if results are available
        avg_bid = avg[0]["average_bid"] if avg else 0
        total_bids = count[0]["total_bids"] if count else 0

        # Return the results
        return {"avg": avg_bid, "count": total_bids, "bids": auctions}

    #SUPPORT
    #every gacha is unique so controlling if it has a current auction on it is sufficient
    def auction_user_presence(self,player_id):
        return False if self.db["auction"].find_one({"player_id":player_id}) is None else True 
    
    def auction_presence(self,auction_id):
        return False if self.db["auction"].find_one({"player_id":auction_id}) is None else True 
    

    def gacha_available(self,player_id,gacha_id):
        return True if self.db["auctions"].find_one[{"player_id":player_id,"gacha_id":gacha_id,"active":True}] else False 

    
        






