import os
import json, yaml
import uvicorn
from database.db import database
import requests
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
import time
from apscheduler.schedulers.background import BackgroundScheduler

unix_time = lambda: int(time.time())

### INIT ###

mock_authentication = None
mock_tux = None
mock_distro = None

mock_player = None
dummy_player_id = "1"

app = FastAPI()
db = database("utils/auctions.json","utils/bids.json")



### CHECKS ###

CHECK_EXPIRY_INTERVAL=1 #in minute
def checkAuctionExpiration():
    print("SCHEDULED FUNCTION")
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

# AUCTION_CREATE_PLAYER
@app.post("/user/auction/auction-create-player", status_code=201)
def auction_create_player(gacha_id:str, starting_price:int, end_time:int):
    check_user(0)

    #arguments check
    if(starting_price<0):raise HTTPException(status_code=400, detail="Invalid price")

    if(unix_time()>=end_time):raise HTTPException(status_code=400, detail="Invalid time")

    #extract player id
    if mock_player:player_id = dummy_player_id
    #remove gacha from player
    if not mock_distro:
        pass

    #add to currently ongoing auctions of the player
    res = db.auction_create_player(player_id,gacha_id,starting_price,end_time)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Invalid User")
    

# AUCTION_DELETE_PLAYER
@app.delete("/user/auction/auction-delete-player", status_code=201)
def auction_delete_player(auction_id):
    check_user(0)

    if mock_player:player_id = dummy_player_id

    #add to currently ongoing auctions of the player
    res = db.auction_delete_player(player_id,auction_id,mock_distro)
    if res == 1: return 0
    elif res == 0: raise HTTPException(status_code=400, detail="No auction found with specified criteria")



# AUCTION_BID_PLAYER
@app.post("/user/auction/auction-bid-player", status_code=201)
def auction_bid(auction_id,bid):
    check_user(0)

    if mock_player:player_id = dummy_player_id

    #extract player id
    res = db.auction_bid(auction_id,player_id,bid,mock_tux)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Auction does not exist")
    elif res == 2: raise HTTPException(status_code=400, detail="Player is owner of auction")
    elif res == 3: raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")


# AUCTION_HISTORY_PLAYER
@app.get("/user/auction/auction-history-player", status_code=200)
def auction_history_player():
    check_user(0)

    if mock_player:player_id = dummy_player_id

    #extract player id
    return db.auction_history_player(player_id)




### ADMIN ###

# AUCTION_HISTORY
@app.get("/admin/auction/auction-history", status_code=200)
def auction_history(player_id:str):
    check_user(1)
    
    #must control presence because db.find() possibly returns []
    if not db.auction_user_presence(player_id):raise HTTPException(status_code=400, detail="Player not present")
    return jsonable_encoder(db.auction_history(player_id))


# AUCTION_MODIFY
@app.put("/admin/auction/auction-modify", status_code=200)
def auction_modify(auction):
    check_user(1)
    
    #must control presence because db.find() possibly returns []
    if not db.auction_presence(auction["auction_id"]):raise HTTPException(status_code=400, detail="Auction not present")
    db.auction_modify(auction)


# AUCTION_DELETE
@app.delete("/admin/auction/auction-delete", status_code=200)
def auction_delete(auction_id):
    check_user(1)
    
    res = db.auction_delete(auction_id,mock_distro)
    if res == 0:raise HTTPException(status_code=400, detail="Auction not present")
    return 0

# AUCTION_INFO
@app.get("/admin/auction/auction-info", status_code=200)
def auction_info(auction_id):
    check_user(1)
        
    res = db.auction_info(auction_id)
    if res is {}:raise HTTPException(status_code=400, detail="Auction not present")
    return res
    

# AUCTION_HISTORY_ALL
@app.get("/admin/auction/auction-history-all")
def auction_history_all():
    check_user(1)
    
    return jsonable_encoder(db.auction_history_all())


# MARKET_ACTIVITY
@app.get("/admin/auction/market-activity", status_code=200)
def market_activity():
    check_user(1)

    return jsonable_encoder(db.market_activity())
'''
if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'))
    '''

## TODO revise endpoint types to and database consistency with such
## see if I have to implement more endpoints