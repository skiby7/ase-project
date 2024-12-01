from pymongo import MongoClient
import json
import uuid
import random
import time
from bson import binary
from utils.util_classes import Auction,Bid,AuctionOptional,BidOptional,IdStrings
from fastapi import Body, FastAPI, HTTPException
from uuid import UUID
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
    
    # TODO a seconda del feedback degli altri
    # AUCTION_CREATE
    def auction_create(self,auction:Auction,mock_distro:bool):
        #TODO controllare che ci sia almeno 1 gacha con gacha_id disponibile da simo
        if not mock_distro:
            pass
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

    
    # DONE
    # AUCTION_DELETE
    #HP auction presence == True (check app-side)
    def auction_delete(self,auction_id:UUID,mock_distro:bool,mock_tux:bool):
        auction = self.db["auctions"].find_one({"auction_id":auction_id}) 
        if not mock_distro:
            #TODO return the bidded gacha
            pass
        if (auction["current_winning_player_id"] is not None) and (not mock_tux):
            #TODO return/unfreeze tux of current winning
            pass

        self.db["auctions"].delete_one({"auction_id":auction_id})
        self.db["bids"].delete_many({"auction_id":auction_id})


    # DONE
    # AUCTION_FILTER
    def auction_filter(self,auction_filter:AuctionOptional):
        if auction_filter.starting_price is not None and auction_filter.starting_price<0:
            raise HTTPException(status_code=400, detail="starting_price must be >=0")
        if auction_filter.current_winning_bid is not None and auction_filter.current_winning_bid<0:
            raise HTTPException(status_code=400, detail="current_winning_bid must be >=0")
        if auction_filter.end_time is not None and auction_filter.end_time<0:
            raise HTTPException(status_code=400, detail="end_time must be >=0")
        
        return list(self.db["auctions"].find(auction_filter.model_dump(),{"_id":0}))


    ##### BID #####

    # BID
    def bid(self,bid:Bid,mock_tux:bool):
        auction = self.db["auctions"].find_one({"auction_id":bid.auction_id,"active":True})
        if auction is None:
            raise HTTPException(status_code=400, detail="Auction does not exist or is not active")
        if bid.auction_id == auction["player_id"]:
            raise HTTPException(status_code=400, detail="Player is owner of auction")
        if bid <= auction["current_winning_bid"]:
            raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")
        
        if not mock_tux:
            #TODO restituire/unfreeze a quello che stava vincendo e prendere/unfreeze quello che vinceva
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

    # DONE
    # BID_FILTER
    def bid_filter(self,bid_filter:BidOptional):
        if bid_filter.bid is not None and bid_filter.bid<0:
            raise HTTPException(status_code=400, detail="bid must be >=0")
        if bid_filter.time is not None and bid_filter.time<0:
            raise HTTPException(status_code=400, detail="time must be >=0")
        
        return self.db["bids"].find(bid_filter.model_dump(),{"_id":0})




    ######### ADMIN #########


    ##### AUCTION #####
    
    '''
    # TODO a seconda del feedback degli altri
    # AUCTION_MODIFY
    def auction_modify(self,auction_id:UUID,auction_modifier:BidOptional):
        
        if auction_modifier.starting_price<0:raise HTTPException(status_code=400, detail="starting_price must be >=0")
        if auction_modifier.current_winning_bid<0:raise HTTPException(status_code=400, detail="current_winning_bid must be >=0")
        if auction_modifier.end_time<0:raise HTTPException(status_code=400, detail="end_time must be >= than current unix_time")

        self.db["auctions"].update_one({"auction_id":auction_id},{"$set":auction_modifier})
    '''
    
    ##### BID #####
    
    '''
    # TODO a seconda del feedback degli altri
    # BID_MODIFY
    def bid_modify(self,bid_id:UUID,bid_modifier:BidOptional):
        if bid_modifier.bid<0:raise HTTPException(status_code=400, detail="starting_price must be >=0")
        if bid_modifier.time<0:raise HTTPException(status_code=400, detail="current_winning_bid must be >=0")
        
        self.db["bid"].update_one({"auction_id":bid_id},{"$set":bid_modifier})
    '''

    # DONE
    # BID_DELETE
    def bid_delete(self,bid_id:UUID,mock_tux:bool):
        bid = self.db["bids"].find_one({"bid_id":bid_id})
        auction = self.db["bids"].find_one({"bid_id":bid["auction_id"]})

        # bid was winning before deletion
        if (bid["player_id"]==auction["current_winning_player_id"]) and (bid["bid"]==auction["current_winning_bid"]):
            
            if not mock_tux:
                #TODO chiamare leo e restituire/unfreezare tux
                pass

            next_highest_bid = self.db["bids"].find_one({"auction_id": bid["auction_id"]},sort=[("bid", -1)])
            if next_highest_bid:
                # update auction
                self.db["auctions"].update_one(
                    {"auction_id": auction["auction_id"]},
                    {
                        "$set": {
                            "current_winning_player_id": next_highest_bid["player_id"],
                            "current_winning_bid": next_highest_bid["bid"]
                        }
                    }
                )
            else:
                # reset winning
                self.db["auctions"].update_one(
                    {"auction_id": auction["auction_id"]},
                    {
                        "$set": {
                            "current_winning_player_id": None,
                            "current_winning_bid": 0
                        }
                    }
                )
        
        self.db["bids"].delete_one({"bid_id":bid_id})
        

    # DONE
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


    ######### SUPPORT #########


    def auction_owner(self,auction_id:UUID):
        owner = self.db["auctions"].find_one({"auction_id":auction_id},{"player_id":1})
        if owner is None:raise HTTPException(status_code=400, detail="No auction found with specified criteria")
        return owner["player_id"]


    def bid_owner(self,bid_id:UUID):
        owner = self.db["bids"].find_one({"bid_id":bid_id},{"bid_id":1})
        if owner is None:raise HTTPException(status_code=400, detail="No bid found with specified criteria")
        return owner["bid_id"]







