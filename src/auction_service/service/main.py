import os
import json, yaml
import uvicorn
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
db = database("utils/distros.json")


CHECK_EXPIRY_INTERVAL=1 #in minute

def checkAuctionExpiry():
    pass

scheduler = BackgroundScheduler()
scheduler.add_job(checkAuctionExpiry,"interval",minutes=CHECK_EXPIRY_INTERVAL)
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
@app.post("/create")
def create(gacha_id,starting_price,end_time):
    check_user(0)

    #arguments check
    if(starting_price<0):raise HTTPException(status_code=400, detail="Invalid User")
    

    if(unix_time()>=end_time):raise HTTPException(status_code=400, detail="Invalid User")

    #extract player id
    #add to currently ongoing auctions of the player
    db.create_auction(player_id,gacha_id,starting_price,end_time)

# place bid on auction
@app.post("/bid")
def bid(auction_id,bid):
    check_user(0)

    #extract player id
    db.bid(auction_id,player_id,bid)

# enable view of auction history
@app.post("/auctionHistory")
def auctionHistory():
    check_user(0)

    #extract player id
    db.auctionHistory(player_id)    

##LOGIC
# Deliver won gacha after auction
# Deliver tux to auction creator after end
# Give back tux if lost auction
#---> service should always watch over currently on going auctions
#---> if time elapsed behave as needed

#NOTES: probably use apscheduler with granularity of whatever
#if microservice is restarted with elapsed auctions has to work the same

#[ADMIN]
##API

# Enable seeing market history of a player
@app.get("/auctionHistoryPlayer")
def auctionHistoryPlayer(player_id):
    #vedere se chi chiama e' un admin
    check_user(1)
        
    db.auctionHistory(player_id)

# Enable to see market auction activity in the last 24h
@app.get("/marketActivity")
def marketActivity():
    #vedere se chi chiama e' un admin
    check_user(1)

    db.marketActivity()

# Enable view details of auction
@app.get("/auctionInfo")
#vedere se chi chiama e' un admin
def auctionInfo(auction_id):
    check_user(1)
        
    db.auctionInfo(auction_id)
    
# Enable manipulation of auction
@app.post("/auctionModify")
def auctionModify(auction):
    #vedere se chi chiama e' un admin
    check_user(1)
    
    db.auctionModify(auction)

# Enable to see all time history
@app.post("/history")
def history():
    #vedere se chi chiama e' un admin
    check_user(1)
    
    return db.auctionHistoryAll()

#[SECURITY]
##LOGIC
# Security - no auction listing manipulations

if __name__ == "__main__":
    init()
