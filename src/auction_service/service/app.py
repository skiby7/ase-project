from database.db import database
from uuid import UUID
from fastapi import Body, FastAPI, HTTPException, Depends
import time
from apscheduler.schedulers.background import BackgroundScheduler
from utils.util_classes import Auction,Bid,AuctionOptional,BidOptional,IdStrings
from utils.check import check_admin,check_user
from auth.access_token_utils import extract_access_token
from auth.access_token_utils import TokenData
from typing import Annotated


unix_time = lambda: int(time.time())

### INIT ###

mock_check = None



#dummy_player_id = "123e4567-e89b-12d3-a456-426614174000"

app = FastAPI()
db = database("database/auctions.json","database/bids.json")



### CHECKS ###

CHECK_EXPIRY_INTERVAL=1 #in minute
def checkAuctionExpiration():
    print("SCHEDULED FUNCTION",flush=True)
    finishedAuctions = db.checkAuctionExpiration()
    for auction in finishedAuctions:
        if not mock_check:break
        #url_api
        #requests.get(url_api)
        #give gacha to winning player
        

scheduler = BackgroundScheduler()
scheduler.add_job(checkAuctionExpiration,"interval",minutes=CHECK_EXPIRY_INTERVAL,coalesce=False,misfire_grace_time=20)
scheduler.start()


# HP for every endpoint: ENDPOINT_NAME - HP IN WHICH IT WORKS





######### ADMIN #########


##### AUCTION #####


# TODO Check if the player exists, maybe is done if gacha is available
# AUCTION_CREATE
@app.post("/auction/admin/auction-create", status_code=201)
def admin_endpoint(auction:Auction,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    print("ciaoooo")
    check_admin(mock_check,token_data)

    db.auction_create(auction,mock_check)


# DONE
# AUCTION_DELETE
@app.delete("/auction/admin/auction-delete", status_code=200)
def admin_endpoint(auction_id:UUID,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_admin(mock_check,token_data)
    
    db.auction_owner(str(auction_id))
    db.auction_delete(str(auction_id),mock_check)


#DONE
# AUCTION_FILTER
@app.get("/auction/admin/auction-filter", status_code=200)
def admin_endpoint(auction_filter:AuctionOptional,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_admin(mock_check,token_data)

    return db.auction_filter(auction_filter)


##### BID #####


# TODO Controllare che il player specificato nel bid esista
# BID_CREATE
@app.post("/auction/admin/bid", status_code=201)
def admin_endpoint(bid: Bid,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_admin(mock_check,token_data)

    db.bid(bid,mock_check)


# BID_DELETE
@app.delete("/auction/admin/bid-delete", status_code=201)
def admin_endpoint(bid_id:UUID,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check,token_data)

    db.bid_owner(bid_id)
    db.bid_delete(str(bid_id),mock_check)


# BID_FILTER
@app.get("/auction/admin/bid-filter", status_code=200)
def admin_endpoint(bid_filter:BidOptional,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_admin(mock_check,token_data)

    return db.bid_filter(bid_filter)


# MARKET_ACTIVITY
@app.get("/auction/admin/market-activity", status_code=200)
def admin_endpoint(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_admin(mock_check,token_data)

    return db.market_activity()




######### PLAYER #########
# HP player can only create and delete auctions (fair for bidders)
# HP player cannot modify created auctions (fair for bidders)
# HP player cannot retire a bid 

##### AUCTION #####


# DONE
# AUCTION_CREATE - player_id == auction.player_id
@app.post("/auction/{player_id}/auction-create", status_code=201)
def player_endpoint(player_id:UUID,auction:Auction,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check,token_data)

    if (player_id != auction.player_id) or ((not mock_check) and str(player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid.")

    db.auction_create(auction,mock_check)
    

# DONE
# AUCTION_DELETE - playerd_id is owner of auction_id
@app.delete("/auction/{player_id}/auction-delete", status_code=200)
def player_endpoint(player_id:UUID,auction_id:UUID,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check,token_data)
    
    if str(player_id) != db.auction_owner(str(auction_id)) or ((not mock_check) and str(player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid.")
    
    db.auction_delete(str(auction_id),mock_check)


# DONE
# AUCTION_FILTER - "active":True
@app.get("/auction/auction-filter", status_code=200)
def player_endpoint(auction_filter:AuctionOptional,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check,token_data)
    
    if auction_filter.active is None or (auction_filter.active is not None and auction_filter.active is False):
        raise HTTPException(status_code=400, detail="Active field must be set to True for player to use this endpoint")
        
    return db.auction_filter(auction_filter)


##### BID #####


# DONE
# AUCTION_BID - player_id == bid.player_id
@app.post("/auction/{player_id}/bid", status_code=201)
def player_endpoint(player_id:UUID,bid:Bid,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check,token_data)

    if (player_id != bid.player_id) or ((not mock_check) and (str(player_id) != token_data.sub)):
        raise HTTPException(status_code=400, detail="Player_id not valid.")

    #extract player id
    db.bid(bid,mock_check)


# DONE
# BID_FILTER - player_id == bid_filter.player_id
@app.get("/auction/{player_id}/bid-filter", status_code=200)
def player_endpoint(player_id:UUID,bid_filter:BidOptional,token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check,token_data)

    if player_id != bid_filter.player_id or ((not mock_check) and str(player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid.")
    
    #extract player id
    return db.bid_filter(bid_filter)
