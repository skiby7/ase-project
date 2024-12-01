import uvicorn
from database.db import database
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


#dummy_player_id = "123e4567-e89b-12d3-a456-426614174000"

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


# HP for every endpoint: ENDPOINT_NAME - HP IN WHICH IT WORKS

######### PLAYER #########
# HP player can only create and delete auctions (fair for bidders)
# HP player cannot modify created auctions (fair for bidders)
# HP player cannot retire a bid 

##### AUCTION #####


# DONE
# AUCTION_CREATE - player_id == auction.player_id
@app.post("/{player_id}/auction/auction-create", status_code=201)
def player_endpoint(player_id:UUID,auction:Auction):
    check_user(0)

    if player_id != auction.player_id:
        raise HTTPException(status_code=400, detail="Cannot create other player's auctions. Set own player_id")

    db.auction_create(auction,mock_distro)
    

# DONE
# AUCTION_DELETE - playerd_id is owner of auction_id
@app.delete("/{player_id}/auction/auction-delete", status_code=200)
def player_endpoint(player_id:UUID,auction_id:UUID):
    check_user(0)

    if player_id != db.auction_owner(auction_id):
        raise HTTPException(status_code=400, detail="Player is not the owner of the specified auction.")
    db.auction_delete(auction_id,False,mock_distro,mock_tux)


# DONE
# AUCTION_FILTER - "active":True
@app.get("/auction/auction-filter", status_code=200)
def player_endpoint(auction_filter:AuctionOptional):
    check_user(0)
    
    if auction_filter.active is not None and auction_filter.active is False:
        raise HTTPException(status_code=400, detail="active field must be set to True for player to use this endpoint")
        
    return db.auction_filter()


##### BID #####


# DONE
# AUCTION_BID - player_id == bid.player_id
@app.post("/{player_id}/auction/bid", status_code=201)
def player_endpoint(player_id:UUID,bid:Bid):
    check_user(0)

    if player_id != bid.player_id:
        raise HTTPException(status_code=400, detail="Cannot bid for other players. Set own player_id")

    #extract player id
    db.bid(bid,mock_tux)


# DONE
# BID_FILTER - player_id == bid_filter.player_id
@app.get("/{player_id}/auction/bid-filter", status_code=200)
def player_endpoint(player_id:UUID,bid_filter:BidOptional):
    check_user(0)

    if player_id != bid_filter.player_id:
        raise HTTPException(status_code=400, detail="Cannot access other player bids data. Set own player_id")
    
    #extract player id
    return db.bid_filter(player_id)




######### ADMIN #########


##### AUCTION #####


# DONE
# AUCTION_CREATE
@app.post("/admin/auction/auction-create", status_code=201)
def player_endpoint(auction:Auction):
    check_user(1)

    db.auction_create(auction,mock_distro)

'''
# DONE
# AUCTION_MODIFY
@app.patch("/admin/auction/auction-modify", status_code=200)
def admin_endpoint(auction_id:UUID,auction_modifier:AuctionOptional):
    check_user(1)
    
    db.auction_owner(auction_id)
    db.auction_modify(auction_id,auction_modifier)
'''

# DONE
# AUCTION_DELETE
@app.delete("/admin/auction/auction-delete", status_code=200)
def admin_endpoint(auction_id:UUID):
    check_user(1)
    
    db.auction_owner(auction_id)
    db.auction_delete(auction_id,mock_distro,mock_tux)


#DONE
# AUCTION_FILTER
@app.get("/admin/auction/auction-filter", status_code=200)
def player_endpoint(auction_filter:AuctionOptional):
    check_user(1)

    return db.auction_filter(auction_filter)


##### BID #####


#DONE
# BID_CREATE
@app.post("/admin/auction/bid", status_code=201)
def player_endpoint(bid: Bid):
    check_user(1)

    db.bid(bid,mock_tux)

'''
# BID_MODIFY
@app.patch("/admin/auction/bid-modify", status_code=200)
def admin_endpoint(bid_id:UUID,bid_modifier:BidOptional):
    check_user(1)
    
    db.bid_owner(bid_id)
    db.bid_modify(bid_id,bid_modifier)
'''

# BID_DELETE
@app.delete("/admin/auction/bid-delete", status_code=201)
def admin_endpoint(bid_id:UUID):
    check_user(0)

    db.bid_owner(bid_id)
    db.bid_delete(bid_id)


# BID_FILTER
@app.get("/admin/auction/bid-filter", status_code=200)
def player_endpoint(bid_filter:BidOptional):
    check_user(1)

    return db.bid_filter(bid_filter)


# MARKET_ACTIVITY
@app.get("/admin/auction/market-activity", status_code=200)
def admin_endpoint():
    check_user(1)

    return db.market_activity()
