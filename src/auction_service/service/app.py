import os
import json, yaml
import uvicorn
from database.db import database
import requests
import uuid
from uuid import UUID
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
import time
from apscheduler.schedulers.background import BackgroundScheduler
from utils.util_classes import Auction,Bid,AuctionOptional,BidOptional,IdStrings
import shared_libs.access_token_utils

unix_time = lambda: int(time.time())

### INIT ###

mock_authentication = None
mock_tux = None
mock_distro = None

mock_player_id = None
dummy_player_id = "123e4567-e89b-12d3-a456-426614174000"

mock_gacha_id = None
dummy_gacha_id = "123e4567-e89b-12d3-a456-426614174000"

mock_bid_id = None
dummy_bid_id = "123e4567-e89b-12d3-a456-426614174000"

mock_auction_id = None
dummy_auction_id = "123e4567-e89b-12d3-a456-426614174000"


app = FastAPI()
db = database("database/auctions.json","database/bids.json")



### CHECKS ###

CHECK_EXPIRY_INTERVAL=1 #in minute
def checkAuctionExpiration():
    print("SCHEDULED FUNCTION",flush=True)
    finishedAuctions = db.checkAuctionExpiration()
    for auction in finishedAuctions:
        if not mock_distro:break
        #url_api
        #requests.get(url_api)
        #give gacha to winning player
        

scheduler = BackgroundScheduler()
scheduler.add_job(checkAuctionExpiration,"interval",minutes=CHECK_EXPIRY_INTERVAL)
scheduler.start()

def check_user(user): #0 USER, 1 ADMIN
    if mock_authentication==True:return True
    if True: #da cambiare
        return True
    else: 
        raise HTTPException(status_code=400, detail="Invalid Admin")


# NB: order is always info > manipulation > active > history

######### PLAYER #########

# HP player can only create and delete auctions (fair for bidders)
# HP player cannot modify created auctions (fair for bidders)
# HP player cannot retire a bid 


##### AUCTION #####

#DONE
# AUCTION_CREATE
@app.post("/{player_id}/auction/auction-create", status_code=201)
def player_endpoint(auction:Auction):
    check_user(0)

    if player_id != auction.player_id:
        raise HTTPException(status_code=400, detail="Cannot create other player's auctions. Set own player_id")
    #extract player id
    if mock_player_id:player_id = dummy_player_id

    #remove gacha from player
    if not mock_distro:
        pass

    #add to currently ongoing auctions of the player
    db.auction_create(auction)
    

# AUCTION_DELETE TODO modificare perche' player_id deve essere checkato e capire se puo' eliminare
@app.delete("/{player_id}/auction/auction-delete", status_code=200)
def player_endpoint(auction_id):
    check_user(0)

    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    if mock_player_id:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)

    res = db.auction_delete_player(player_id,auction_id,mock_distro)
    if res == 1: return 0
    elif res == 0: raise HTTPException(status_code=400, detail="No auction found with specified criteria")

#DONE
# AUCTION_FILTER - usable only on active auction
@app.get("/auction/auction-filter", status_code=200)
def player_endpoint(auction_filter:AuctionOptional):
    check_user(0)
    
    if auction_filter.active is not None and auction_filter.active is False:
        raise HTTPException(status_code=400, detail="active field must be set to True to use this endpoint")
        
    #extract player id
    return db.auction_filter()


##### BID #####

#DONE
# AUCTION_BID
@app.post("/{player_id}/auction/bid", status_code=201)
def player_endpoint(bid:Bid):
    check_user(0)

    if player_id != bid.player_id:
        raise HTTPException(status_code=400, detail="Cannot bid for other players. Set own player_id")
    if mock_player_id:player_id = dummy_player_id

    #extract player id
    db.bid(bid,mock_tux)

#DONE
# BID_FILTER - usable only if using player corresponds to the player in filter
@app.get("/{player_id}/auction/bid-filter", status_code=200)
def player_endpoint(bid_filter:BidOptional):
    check_user(0)

    if mock_player_id:player_id = dummy_player_id
    if player_id != bid_filter.player_id:
        raise HTTPException(status_code=400, detail="Cannot access other player bids data. Set own player_id")
    
    #extract player id
    return db.bid_filter(player_id)




######### ADMIN #########


##### AUCTION #####

#DONE
# AUCTION_CREATE
@app.post("/admin/auction/auction-create", status_code=201)
def player_endpoint(auction:Auction):
    check_user(0)

    #remove gacha from player
    if not mock_distro:
        pass

    #add to currently ongoing auctions of the player
    db.auction_create(auction)


# AUCTION_MODIFY
@app.patch("/admin/auction/auction-modify", status_code=200)
def admin_endpoint(auction_id:str,auction_modifier:AuctionOptional):
    check_user(1)
    
    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    if auction_modifier.starting_price<0:raise HTTPException(status_code=400, detail="starting_price must be >=0")
    if auction_modifier.current_winning_bid<0:raise HTTPException(status_code=400, detail="current_winning_bid must be >=0")
    if auction_modifier.end_time<0:raise HTTPException(status_code=400, detail="end_time must be >=0")

    #must control presence because db.find() possibly returns []
    if not db.auction_presence(auction_id):raise HTTPException(status_code=400, detail="Auction not present")
    db.auction_modify(auction_id,auction_modifier)


# AUCTION_DELETE
@app.delete("/admin/auction/auction-delete", status_code=200)
def admin_endpoint(auction_id):
    check_user(1)
    
    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    res = db.auction_delete(auction_id,mock_distro)
    if res == 0:raise HTTPException(status_code=400, detail="Auction not present")
    return 0

#DONE
# AUCTION_FILTER
@app.get("/admin/auction/auction-filter", status_code=200)
def player_endpoint(auction_filter:AuctionOptional):
    check_user(1)

    if mock_player_id:player_id = dummy_player_id
    
    #extract player id
    return db.auction_filter(auction_filter)


##### BID #####

#DONE
# BID_CREATE
@app.post("/admin/auction/bid", status_code=201)
def player_endpoint(bid: Bid):
    check_user(1)

    if mock_player_id:player_id = dummy_player_id

    #extract player id
    db.bid(bid,mock_tux)


# BID_MODIFY
@app.patch("/admin/auction/bid-modify", status_code=200)
def admin_endpoint(bid_id:str,bid_modifier:BidOptional):
    check_user(1)
    
    is_valid_id(bid_id,IdStrings.BID_ID)
    #must control presence because db.find() possibly returns []
    if not db.bid_presence(bid_id):raise HTTPException(status_code=400, detail="Bid not present")
    db.bid_modify(bid_id,bid_modifier)


# BID_DELETE
@app.delete("/admin/auction/bid-delete", status_code=201)
def admin_endpoint(bid_id):
    check_user(0)

    is_valid_id(bid_id,IdStrings.BID_ID)

    res = db.bid_delete(bid_id)
    if res == 1: return 0
    elif res == 0: raise HTTPException(status_code=400, detail="No bid found with specified bid_id")


# BID_FILTER
@app.get("/admin/auction/bid-filter", status_code=200)
def player_endpoint(bid_filter:BidOptional):
    check_user(1)

    if mock_player_id:player_id = dummy_player_id
    
    #extract player id
    return db.bid_filter(bid_filter)


# BID_HISTORY_PLAYER - same as player
# BID_HISTORY_PLAYER_AUCTION - same as player
# BID_HISTORY_AUCTION
# BID_HISTORY

# MARKET_ACTIVITY
@app.get("/admin/auction/market-activity", status_code=200)
def admin_endpoint():
    check_user(1)

    return db.market_activity()
'''
if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'))
    '''

## TODO revise endpoint types to and database consistency with such
## see if I have to implement more endpoints

### SUPPORT ###

def is_valid_uuid(input_string: str) -> bool:
    try:
        uuid_obj = uuid.UUID(input_string)
        return str(uuid_obj) == input_string.lower()
    except ValueError:
        return False

def is_valid_id(id,attribute):
    if not is_valid_uuid(id):raise HTTPException(status_code=400, detail="Invalid"+attribute)
