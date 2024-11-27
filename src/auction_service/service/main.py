import os
import json, yaml
import uvicorn
import database.db
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from apscheduler import BackgroundScheduler
unix_time = lambda: int(time.time())

### App init ###
app = FastAPI()

### DB init ###
db = database("utils/auctions.json","utils/bids.json")

##LOGIC
# Deliver won gacha after auction
# Deliver tux to auction creator after end
# Give back tux if lost auction
#---> service should always watch over currently on going auctions
#---> if time elapsed behave as needed

CHECK_EXPIRY_INTERVAL=1 #in minute

def checkAuctionExpiration():
    finishedAuctions = db.checkAuctionExpiry()
    for auction in finishedAuctions:
        #notify
        pass

scheduler = BackgroundScheduler()
scheduler.add_job(checkAuctionExpiration,"interval",minutes=CHECK_EXPIRY_INTERVAL)
scheduler.start()


### Implementation ###

def check_user(user): #0 USER, 1 ADMIN
    if True: #da cambiare
        return True
    else: 
        raise HTTPException(status_code=400, detail="Invalid Admin")

#[PLAYER]
##API

# create auction
@app.post("/user/auction/auction-create", status_code=201)
def auction_create(gacha_id,starting_price,end_time):
    check_user(0)

    #arguments check
    if(starting_price<0):raise HTTPException(status_code=400, detail="Invalid User")
    

    if(unix_time()>=end_time):raise HTTPException(status_code=400, detail="Invalid User")

    #extract player id
    #add to currently ongoing auctions of the player
    db.auction_create(db,player_id,gacha_id,starting_price,end_time)

# place bid on auction
@app.post("/user/auction/auction-bid", status_code=201)
def auction_bid(auction_id,bid):
    check_user(0)

    #extract player id
    db.auction_bid(db,auction_id,player_id,bid)

# enable view of auction history
@app.get("/user/auction/auction-history", status_code=200)
def auction_history():
    check_user(0)

    #extract player id
    db.auction_history(player_id)    

#[ADMIN]
##API

# Enable seeing market history of a player
@app.get("/admin/auction/auction-history-player", status_code=200)
def auction_history_player(player_id):
    #vedere se chi chiama e' un admin
    check_user(1)
        
    db.auction_history_player(db,player_id)

# Enable view details of auction
@app.get("/admin/auction/auction-info", status_code=200)
#vedere se chi chiama e' un admin
def auction_info(auction_id):
    check_user(1)
        
    db.auction_info(db,auction_id)
    
# Enable manipulation of auction
@app.put("/admin/auction/auction-modify", status_code=200)
def auction_modify(auction):
    #vedere se chi chiama e' un admin
    check_user(1)
    
    db.auction_modify(db,auction)

# Enable to see all time history
@app.get("/auction-history-all")
def auction_history_all():
    #vedere se chi chiama e' un admin
    check_user(1)
    
    return db.auction_history_all(db)

# Enable to see market auction activity in the last 24h
@app.get("/admin/auction/market-activity", status_code=200)
def market_activity():
    #vedere se chi chiama e' un admin
    check_user(1)

    db.market_activity(db)

#[SECURITY]
##LOGIC
# Security - no auction listing manipulations

if __name__ == "__main__":
    init()
