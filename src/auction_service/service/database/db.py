from pymongo import MongoClient
import json
import uuid
import time
from utils.util_classes import Auction,Bid,AuctionOptional,BidOptional,IdStrings
from fastapi import Body, FastAPI, HTTPException
from uuid import UUID
unix_time = lambda: int(time.time())




class database:
    def __init__(self,auctionsFile,bidsFile):
        self.auctionsFile = auctionsFile
        self.bidsFile = bidsFile

        username = "root"
        host = "db"
        port = "27017"
        db = "admin"
        database = "mydatabase"
        with open('/run/secrets/pw', 'r') as file:
            password = file.read().strip()
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={db}&tls=true&tlsAllowInvalidCertificates=true"
        self.client = MongoClient(uri)
        
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
    def auction_create(self,auction:Auction,mock_check:bool):
        #TODO controllare che ci sia almeno 1 gacha con gacha_id disponibile da simo
        #TODO controllare che il player esista
        if not mock_check:
            pass
        if(auction.starting_price<0):
            raise HTTPException(status_code=400, detail="Invalid price")
        if(auction.end_time<unix_time()):
            raise HTTPException(status_code=400, detail="Invalid time")
        
        if mock_check:
            id=str(UUID("00000000-0000-4000-8000-000000000000"))
        else:
            while(True):
                id=str(uuid.uuid4())
                if(not self.db["auctions"].find_one({"auction_id":id})):break
            
        auction={
            "auction_id":str(id),
            "player_id":str(auction.player_id),
            "gacha_id":str(auction.gacha_id),
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
    def auction_delete(self,auction_id:str,mock_check:bool):
        auction = self.db["auctions"].find_one({"auction_id":auction_id}) 
        #TODO return the bidded gacha
        if not mock_check:
            
            pass

        #TODO return/unfreeze tux of current winning
        if (not mock_check) and (auction["current_winning_player_id"] is not None):
            
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
        
        filtered_dict = {
            key: (str(value) if isinstance(value, UUID) else value)
            for key, value in auction_filter.model_dump().items()
            if value is not None
        }
        return list(self.db["auctions"].find(filtered_dict,{"_id":0}))


    ##### BID #####

    # DONE
    # BID
    def bid(self,bid:Bid,mock_check:bool):
        auction = self.db["auctions"].find_one({"auction_id":str(bid.auction_id),"active":True})
        if auction is None:
            raise HTTPException(status_code=400, detail="Auction does not exist or is not active")
        if str(bid.player_id) == auction["player_id"]:
            raise HTTPException(status_code=400, detail="Player is owner of auction")
        if bid.bid <= auction["current_winning_bid"]:
            raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")
        
        if not mock_check:
            #TODO restituire/unfreeze a quello che stava vincendo e prendere/unfreeze quello che vinceva
            pass
        
        update={}
        update["current_winning_player_id"]=str(bid.player_id)
        update["current_winning_bid"]=bid.bid
        self.db["auctions"].update_one({},{"$set": update})

        bidInsert = bid.model_dump()
        if mock_check:
            id=str(UUID("00000000-0000-4000-8000-000000000000"))
        else:
            while(True):
                id=str(uuid.uuid4())
                if(not self.db["auctions"].find_one({"auction_id":id})):break
        bidInsert["bid_id"]=id
        bidInsert["time"]=unix_time()
        bidInsert = {
            key: (str(value) if isinstance(value, UUID) else value)
            for key, value in bidInsert.items()
        }
        
        self.db["bids"].insert_one(bidInsert)

    # DONE
    # BID_FILTER
    def bid_filter(self,bid_filter:BidOptional):
        if bid_filter.bid is not None and bid_filter.bid<0:
            raise HTTPException(status_code=400, detail="bid must be >=0")
        if bid_filter.time is not None and bid_filter.time<0:
            raise HTTPException(status_code=400, detail="time must be >=0")
        
        filtered_dict = {
            key: (str(value) if isinstance(value, UUID) else value)
            for key, value in bid_filter.model_dump().items()
            if value is not None
        }
        print("caiao",filtered_dict,type(filtered_dict))
        return list(self.db["bids"].find(filtered_dict,{"_id":0}))




    ######### ADMIN #########

    ##### BID #####


    # DONE
    # BID_DELETE
    def bid_delete(self,bid_id:str,mock_check:bool):
        bid = self.db["bids"].find_one({"bid_id":bid_id})
        auction = self.db["bids"].find_one({"bid_id":bid["auction_id"]})

        # bid was winning before deletion
        if (bid["player_id"]==auction["current_winning_player_id"]) and (bid["bid"]==auction["current_winning_bid"]):
            
            if not mock_check:
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
        return {"avg": avg_bid, "count": total_bids, "bids": list(auctions)}


    ######### SUPPORT #########


    def auction_owner(self,auction_id:str):
        owner = self.db["auctions"].find_one({"auction_id":auction_id},{"player_id":1})
        if owner is None:raise HTTPException(status_code=400, detail="No auction found with specified criteria")
        return owner["player_id"]


    def bid_owner(self,bid_id:str):
        owner = self.db["bids"].find_one({"bid_id":bid_id},{"bid_id":1})
        if owner is None:raise HTTPException(status_code=400, detail="No bid found with specified criteria")
        return owner["bid_id"]







