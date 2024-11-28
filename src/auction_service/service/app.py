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

### INIT ###

mock_authentication = None
mock_tux = None
mock_distro = None
app = FastAPI()
db = database("utils/auctions.json","utils/bids.json")



### CHECKS ###

CHECK_EXPIRY_INTERVAL=1 #in minute
def checkAuctionExpiration():
    finishedAuctions = db.checkAuctionExpiry()
    for auction in finishedAuctions:
        if not mock_distro:break
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

# AUCTION_CREATE
@app.post("/user/auction/auction-create", status_code=201)
def auction_create(gacha_id,starting_price,end_time):
    check_user(0)

    #arguments check
    if(starting_price<0):raise HTTPException(status_code=400, detail="Invalid price")

    if(unix_time()>=end_time):raise HTTPException(status_code=400, detail="Invalid time")

    #extract player id
    #remove gacha from player
    if not mock_distro:pass

    #add to currently ongoing auctions of the player
    res = db.auction_create(db,player_id,gacha_id,starting_price,end_time)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Invalid User")
    

# AUCTION_BID
@app.post("/user/auction/auction-bid", status_code=201)
def auction_bid(auction_id,bid):
    check_user(0)

    #extract player id
    res = db.auction_bid(db,auction_id,player_id,bid,mock_tux)
    if res == 0: return res
    elif res == 1: raise HTTPException(status_code=400, detail="Auction does not exist")
    elif res == 2: raise HTTPException(status_code=400, detail="Player is owner of auction")
    elif res == 3: raise HTTPException(status_code=400, detail="Bid must be higher than currently winning bid")


# AUCTION_HISTORY
@app.get("/user/auction/auction-history", status_code=200)
def auction_history():
    check_user(0)

    #extract player id
    db.auction_history(player_id)




### ADMIN ###

# AUCTION_HISTORY_PLAYER
@app.get("/admin/auction/auction-history-player", status_code=200)
def auction_history_player(player_id):
    #vedere se chi chiama e' un admin
    check_user(1)
    
    if not db.auction_user_presence(db,player_id):raise HTTPException(status_code=400, detail="Player not present")
    return db.auction_history_player(db,player_id)


# AUCTION_INFO
@app.get("/admin/auction/auction-info", status_code=200)
def auction_info(auction_id):
    check_user(1)
        
    if not db.auction_presence(db,auction_id):raise HTTPException(status_code=400, detail="Auction not present")
    db.auction_info(db,auction_id)
    

# AUCTION_MODIFY
@app.put("/admin/auction/auction-modify", status_code=200)
def auction_modify(auction):
    #vedere se chi chiama e' un admin
    check_user(1)
    
    if not db.auction_presence(db,auction["auction_id"]):raise HTTPException(status_code=400, detail="Auction not present")
    db.auction_modify(db,auction)


# AUCTION_HISTORY_ALL
@app.get("/admin/auction/auction-history-all")
def auction_history_all():
    #vedere se chi chiama e' un admin
    check_user(1)
    
    return db.auction_history_all(db)


# MARKET_ACTIVITY
@app.get("/admin/auction/market-activity", status_code=200)
def market_activity():
    #vedere se chi chiama e' un admin
    check_user(1)

    return db.market_activity(db)
'''
if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'))
    '''