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
    def __init__(self,auctionsFile):
        self.auctionsFile = auctionsFile
        self.bidsFile = bidsFile
        self.client = MongoClient("db", 27017, maxPoolSize=50)
        self.db = self.client["mydatabase"]
        if "auctions" in self.db.list_collection_names():
            print(" \n\n DB ACTIVE  \n\n")
        else: 
            self.db_inizialization()
        

    # convert to json distro.txt
    def db_init_supp(collection,file):
        with open(file, "r") as file:
            data = json.load(file)
            gachas.insert_many(data)

    def db_inizialization(self):
        self.db.create_collection("auctions")
        auctions = self.db["auctions"]

        self.db.create_collection("bids")
        bids = self.db["bids"]

        db_init_supp(auctions,self.auctionsFile)
        db_init_supp(bids,self.bidsFile)

    #PLAYER
    def get_user_auction_history(uuid):
        return list( self.db["bids"].find({"uuid":uuid}) )
    
    def create_auction(player_id,gacha_id,starting_price,end_time):
        #control if gacha is already in bid
        if(!self.gacha_available(gacha_id)){
            return 1
        }
        while(True){
            id=uuid.uuid4()
            if(!self.db["auctions"].find_one({"auction_id":id}))break
        }
        auction={
            "auction_id":id,
            "player_id":player_id,"gacha_id":gacha_id,
            "starting_price":starting_price,
            "current_winning_player_id":None,
            "current_winning_bid":0
            "end_time":end_time
            "active":True
            }

        self.db["auctions"].insert_one(auction)
        return 0

    def bid(auction_id,player_id,bid):
        auction = self.db["auctions"].find_one({"auction_id":id,"active":True})
        if auction is None:return -1
        if player_id == auction["player_id"]: return -1
        if bid <= auction["current_winning_bid"]:return -1

        auction["time"]=unix_time()
        auction["current_winning_player_id"]=player_id
        auction["current_winning_bid"]=bid

        self.db["bids"].insert_one({"player_id":player_id,"auction_id":auction_id,"bid":bid})
    
    def auctionHistory(player_id):
        supp = list(self.db["auctions"].find({"player_id":}))
        return [{"auction_id": auction["auction_id"],"player_id": auction["player_id"],"gacha_id": auction["auction_id"]} for auction in supp]
    

    #ADMIN
    #NB - because these are used by admins they contain _id
    def auctionInfo(auction_id):
        return self.db["auctions"].find_one({"auction_id":auction_id})

    def auctionModify(auction):
        self.db["auctions"].update_one({"player_id":auction["player_id"]},{"$set":auction})
    
    def auctionHistoryAll():
        return list(self.db["auctions"].find())
    
    def marketActivity():
        twenty_four_hours_ago = current_time - 86400
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
        avg_bid = avg[0]["average_bid"] if avg else None
        total_bids = count[0]["total_bids"] if count else 0

        # Return the results
        return {"avg": avg_bid, "count": total_bids, "bids": auctions}

    
    #SUPPORT
    #every gacha is unique so controlling if it has a current auction on it is sufficient
    def gacha_available(gacha_id):
        return self.db["auctions"].find_one[{"gacha_id":gacha_id,"active":True}]?False:True

    
        






