from pymongo import MongoClient
import json
import uuid
import random
import time
from bson import binary
from utils.util_classes import Auction,Bid,AuctionOptional,BidOptional,IdStrings
from fastapi import Body, FastAPI, HTTPException
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




    ######### PLAYER #########


    ##### AUCTION #####
    
    #DONE
    def auction_create(self,auction:Auction):
        #control if gacha is already in bid
        #da fare con simo
        # if(not self.gacha_available(self,player_id,gacha_id)):return 1
        if(auction.starting_price<0):
            raise HTTPException(status_code=400, detail="Invalid price")
        if(auction.end_time<unix_time()):
            raise HTTPException(status_code=400, detail="Invalid time")
        

        while(True):
            id=str(uuid.uuid4())
            if(not self.db["auctions"].find_one({"auction_id":id})):break
        
        auction={
            "auction_id":id,
            "player_id":auction.player_id,
            "gacha_id":auction.gacha_id,
            "starting_price":auction.starting_price,
            "current_winning_player_id":None,
            "current_winning_bid":0,
            "end_time":auction.end_time,
            "active":True
            }

        self.db["auctions"].insert_one(auction)
        return 0


    def auction_delete(self,auction_id,mock_distro):
        #return the bidded gacha
        if not mock_distro:
            pass

        return self.db["auctions"].delete_one({"player_id":player_id,"auction_id":auction_id})
        
    #DONE
    def auction_filter(self,auction_filter:AuctionOptional):
        if auction_filter.starting_price is not None and auction_filter.starting_price<0:
            raise HTTPException(status_code=400, detail="starting_price must be >=0")
        if auction_filter.current_winning_bid is not None and auction_filter.current_winning_bid<0:
            raise HTTPException(status_code=400, detail="current_winning_bid must be >=0")
        if auction_filter.end_time is not None and auction_filter.end_time<0:
            raise HTTPException(status_code=400, detail="end_time must be >=0")
        
        return self.db["auctions"].find(auction_filter.model_dump(),{"_id":0})


    ##### BID #####

    #DONE
    def bid(self,bid:Bid,mock_tux):
        auction = self.db["auctions"].find_one({"auction_id":bid.auction_id,"active":True})
        if auction is None:
            raise HTTPException(status_code=400, detail="Auction does not exist")
        if bid.auction_id == auction["player_id"]:
            raise HTTPException(status_code=400, detail="Player is owner of auction")
        if bid <= auction["current_winning_bid"]:
            raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")
        
        if not mock_tux:
            #restituire i soldi al player che stava vincendo 
            # e prendere quello che ha biddato
            pass
        
        update={}
        update["current_winning_player_id"]=bid.player_id
        update["current_winning_bid"]=bid
        self.db["auctions"].update_one({},{"$set": update})

        bidInsert = bid.model_dump()
        while(True):
            id=str(uuid.uuid4())
            if(not self.db["bids"].find_one({"bid_id":id})):break
        bidInsert["bid_id"]=id
        bidInsert["time"]=unix_time()
        self.db["bids"].insert_one(bidInsert)
        return 0

    #DONE
    def bid_filter(self,bid_filter:BidOptional):
        if bid_filter.bid is not None and bid_filter.bid<0:
            raise HTTPException(status_code=400, detail="bid must be >=0")
        if bid_filter.time is not None and bid_filter.time<0:
            raise HTTPException(status_code=400, detail="time must be >=0")
        
        return self.db["bids"].find(bid_filter.model_dump(),{"_id":0})




    ######### ADMIN #########


    ##### AUCTION #####
    
    def auction_modify(self,auction_id,auction_modifier):
        #scoprire come rimuovere campi a None dal modifier
        self.db["auctions"].update_one({"auction_id":auction["auction_id"]},{"$set":auction})
        
    
    ##### BID #####
    #TODO bid_delete  (ricordarsi di fare il fallback sul bet minore),e tutto il resto
    #per entrambi
    
    # BID_MODIFY
    def bid_modify(self,bid):
        #self.db["bid"].update_one({"auction_id":bid["auction_id"],"player_id":bid["player_id"]},{"$set":bid})


    # BID_DELETE
    def bid_delete(self,bid_id):
        return self.db["bids"].delete_one({"bid_id":bid["bid_id"]})
        

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
    
    #TODO FARE 2 FUZNIONI SUPPORT PER DELETE CERCARE SE AUCTION E BID APPARTENGONO A PLAYER SPECIFICATO






