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
from utils.util_classes import Auction,AuctionModifier,Bid,BidModifier,IdStrings
import shared_libs.access_token_utils

unix_time = lambda: int(time.time())

### INIT ###

mock_authentication = None
mock_tux = None
mock_distro = None

mock_player = None
dummy_player_id = "123e4567-e89b-12d3-a456-426614174000"

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




### PLAYER ###
# HP player can only create and delete auctions (fair for bidders)
# HP player cannot modify created auctions (fair for bidders)
# HP player cannot retire a bid 

# AUCTION_CREATE_PLAYER
@app.post("/{player_id}/auction/auction-create", status_code=201)
def player_endpoint(gacha_id:str, starting_price:int, end_time:int):
    check_user(0)

    is_valid_id(gacha_id,IdStrings.GACHA_ID)
    if(starting_price<0):raise HTTPException(status_code=400, detail="Invalid price")
    if(unix_time()>=end_time):raise HTTPException(status_code=400, detail="Invalid time")

    #extract player id
    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)

    #remove gacha from player
    if not mock_distro:
        pass

    #add to currently ongoing auctions of the player
    res = db.auction_create(player_id,gacha_id,starting_price,end_time)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Invalid User")
    

# AUCTION_DELETE
@app.delete("/{player_id}/auction/auction-delete", status_code=201)
def player_endpoint(auction_id):
    check_user(0)

    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)


    #add to currently ongoing auctions of the player
    res = db.auction_delete(player_id,auction_id,mock_distro)
    if res == 1: return 0
    elif res == 0: raise HTTPException(status_code=400, detail="No auction found with specified criteria")


# AUCTION_BID
@app.post("/{player_id}/auction/auction-bid", status_code=201)
def player_endpoint(auction_id,bid):
    check_user(0)

    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)

    #extract player id
    res = db.auction_bid(auction_id,player_id,bid,mock_tux)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Auction does not exist")
    elif res == 2: raise HTTPException(status_code=400, detail="Player is owner of auction")
    elif res == 3: raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")


# AUCTION_ACTIVE
@app.get("/{player_id}/auction/auction-active", status_code=200)
def player_endpoint():
    check_user(0)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    
    #extract player id
    return db.auction_active(player_id)


# AUCTION_ACTIVE_ALL
@app.get("/{player_id}/auction-active-all", status_code=200)
def player_endpoint(player_id:str):
    check_user(0)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    
    #extract player id
    return db.bid_history_auction()


# AUCTION_HISTORY
@app.get("/{player_id}/auction/auction-history-player", status_code=200)
def player_endpoint(player_id:str):
    check_user(0)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)

    if not is_valid_uuid(player_id):raise HTTPException(status_code=400, detail="Invalid player_id")
    return db.auction_history_player(player_id)


# BID_HISTORY
@app.get("/{player_id}/auction/bid-history", status_code=200)
def player_endpoint():
    check_user(0)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    
    #extract player id
    return db.bid_history(player_id)


# BID_HISTORY_AUCTION
@app.get("/{player_id}/auction/{auction_id}/bid-history", status_code=200)
def player_endpoint(player_id:str,auction_id:str):
    check_user(0)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    
    #extract player id
    return db.bid_history_player_auction(player_id,auction_id)




######### ADMIN #########


##### AUCTION #####

# AUCTION_INFO
@app.get("/admin/auction/auction-info", status_code=200)
def admin_endpoint(auction_id):
    check_user(1)
        
    is_valid_id(auction_id,IdStrings.AUCTION_ID)

    res = db.auction_info(auction_id)
    if res is {}:raise HTTPException(status_code=400, detail="Auction not present")
    return res
    

# AUCTION_CREATE
@app.post("/admin/auction/auction-create", status_code=201)
def player_endpoint(player_id:str,gacha_id:str, starting_price:int, end_time:int):
    check_user(1)

    is_valid_id(gacha_id,IdStrings.GACHA_ID)
    if(starting_price<0):raise HTTPException(status_code=400, detail="Invalid price")
    if(unix_time()>=end_time):raise HTTPException(status_code=400, detail="Invalid time")

    #extract player id
    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)

    #remove gacha from player
    if not mock_distro:
        pass

    #add to currently ongoing auctions of the player
    res = db.auction_create(player_id,gacha_id,starting_price,end_time)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Invalid User")



# AUCTION_MODIFY
@app.patch("/admin/auction/auction-modify", status_code=200)
def admin_endpoint(auction_id:str,auction_modifier:AuctionModifier):
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


# AUCTION_ACTIVE
@app.get("/admin/auction/auction-active", status_code=200)
def player_endpoint(player_id:str):
    check_user(1)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    
    #extract player id
    return db.auction_active(player_id)


# AUCTION_ACTIVE_ALL
@app.get("/admin/auction-active-all", status_code=200)
def player_endpoint():
    check_user(1)
    
    return db.auction_active_all()


# AUCTION_HISTORY_PLAYER
@app.get("/admin/auction/auction-history-player", status_code=200)
def admin_endpoint(player_id:str):
    check_user(1)

    is_valid_id(player_id,IdStrings.PLAYER_ID)
    #must control presence because db.find() possibly returns []
    if not db.auction_user_presence(player_id):raise HTTPException(status_code=400, detail="Player not present")
    return db.auction_history(player_id)


# AUCTION_HISTORY
@app.get("/admin/auction/auction-history")
def admin_endpoint():
    check_user(1)
    
    return db.auction_history()


##### BID #####

# BID_CREATE TODO MODIFICARE 
@app.post("/admin/auction/bid-create", status_code=201)
def player_endpoint(bid: Bid):
    check_user(1)

    is_valid_id(bid["bid_id"],IdStrings.BID_ID)
    is_valid_id(bid["auction_id"],IdStrings.AUCTION_ID)
    is_valid_id(bid["player_id"],IdStrings.PLAYER_ID)
    if bid["bid"]<0:raise HTTPException(status_code=400, detail="bid must be a number higher than 0")
    if bid["time"]<0:raise HTTPException(status_code=400, detail="time must be a number higher than 0")

    #extract player id
    res = db.bid_create(bid["auction_id"],player_id,bid,mock_tux)
    if res == 0: return res
    #should be changed
    elif res == 1: raise HTTPException(status_code=400, detail="Auction does not exist")
    elif res == 2: raise HTTPException(status_code=400, detail="Player is owner of auction")
    elif res == 3: raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")


# BID_MODIFY
@app.patch("/admin/auction/bid-modify", status_code=200)
def admin_endpoint(bid_id:str,bid_modifier:BidModifier):
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

    #add to currently ongoing auctions of the player
    res = db.bid_delete(bid_id)
    if res == 1: return 0
    elif res == 0: raise HTTPException(status_code=400, detail="No bid found with specified bid_id")


# BID_HISTORY_PLAYER - same as player
@app.get("/admin/auction/bid-history-player", status_code=200)
def admin_endpoint(player_id:str):
    check_user(1)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    
    #extract player id
    return db.bid_history_player(player_id)


# BID_HISTORY_PLAYER_AUCTION - same as player
@app.get("/admin/auction/{auction_id}/bid-history", status_code=200)
def admin_endpoint(player_id:str,auction_id:str):
    check_user(1)

    if mock_player:player_id = dummy_player_id
    is_valid_id(player_id,IdStrings.PLAYER_ID)
    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    
    #extract player id
    return db.bid_history_auction(player_id,auction_id)


# BID_HISTORY_AUCTION
@app.get("/admin/auction/bid-history-player", status_code=200)
def admin_endpoint(auction_id:str):
    check_user(1)

    if mock_player:player_id = dummy_player_id
    is_valid_id(auction_id,IdStrings.AUCTION_ID)
    
    #extract player id
    return db.bid_history_player_auction(player_id)


# BID_HISTORY
@app.get("/admin/bid-history", status_code=200)
def admin_endpoint():
    check_user(1)
    
    return db.bid_history()


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
