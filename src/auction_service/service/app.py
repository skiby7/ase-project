import logging

from database.db import database
from uuid import UUID
from fastapi import Body, FastAPI, HTTPException, Depends, Query
import time
from apscheduler.schedulers.background import BackgroundScheduler
from utils.util_classes import AuctionCreate, Bid, AuctionOptional, BidOptional, AuthId
from utils.check import check_admin, check_user
from auth.access_token_utils import extract_access_token
from auth.access_token_utils import TokenData
from typing import Annotated

unix_time = lambda: int(time.time())

### INIT ###

mock_check = False

# dummy_player_id = "123e4567-e89b-12d3-a456-426614174000"

app = FastAPI()
db = database("database/auctions.json", "database/bids.json", "database/users.json")

### CHECKS ###

CHECK_EXPIRY_INTERVAL_MINUTES = 1  # in minute
CHECK_EXPIRY_INTERVAL_SECONDS = 2


def checkAuctionExpiration():
    finishedAuctions = db.checkAuctionExpiration()
    for auction in finishedAuctions:
        auction_id = auction["auction_id"];
        logging.info(f"Handling expired auction {auction_id}")
        # db.collection["auctions"].update_one({"player_id":auction["player_id"]},{"$set":{"active":False}})
        if mock_check: continue
        token_data = db.auth_get_admin_token()
        db.gacha_add_gacha(str(auction["current_winning_player_id"]), str(auction["gacha_name"]), token_data)
        db.tux_settle_auction(str(auction["auction_id"]), str(auction["current_winning_player_id"]),
                              str(auction["player_id"]), token_data)


scheduler = BackgroundScheduler()
scheduler.add_job(checkAuctionExpiration, "interval", seconds=CHECK_EXPIRY_INTERVAL_SECONDS, coalesce=False,
                  misfire_grace_time=20)
scheduler.start()


# HP for every endpoint: ENDPOINT_NAME - HP IN WHICH IT WORKS


######### ADMIN #########


##### AUCTION #####


# AUCTION_CREATE
@app.post("/admin/auctions/", status_code=201)
def admin_auction_create(token_data: Annotated[TokenData, Depends(extract_access_token)], auction: AuctionCreate = Body()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.auction_create(auction, mock_check)


# DONE
# AUCTION_DELETE
@app.delete("/admin/auctions/{auction_id}", status_code=200)
def admin_auction_delete(auction_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.auction_owner(str(auction_id))
    db.auction_delete(str(auction_id), mock_check)
    return {"details":"Success!"}


# DONE
# AUCTION_FILTER
@app.get("/admin/auctions", status_code=200)
def admin_auction_filter(token_data: Annotated[TokenData, Depends(extract_access_token)],
                   auction_filter: AuctionOptional = Query()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.auction_filter(auction_filter)


##### BID #####


# TODO Controllare che il player specificato nel bid esista
# BID_CREATE
@app.post("/admin/bids", status_code=201)
def admin_bid(token_data: Annotated[TokenData, Depends(extract_access_token)], bid: Bid = Body()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.bid(bid, mock_check)
    return {"details":"Success!"}


# BID_FILTER
@app.get("/admin/auctions/{auction_id}/bids", status_code=200)
def admin_bid_filter(token_data: Annotated[TokenData, Depends(extract_access_token)], bid_filter: BidOptional = Query()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.bid_filter(bid_filter)


# MARKET_ACTIVITY
@app.get("/admin/auctions/activity", status_code=200)
def admin_market_activity(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.market_activity()


######### PLAYER #########
# HP player can only create and delete auctions (fair for bidders)
# HP player cannot modify created auctions (fair for bidders)
# HP player cannot retire a bid

##### AUCTION #####


# DONE
# AUCTION_CREATE - player_id == auction.player_id
@app.post("/auctions", status_code=201)
def player_endpoint(token_data: Annotated[TokenData, Depends(extract_access_token)], auction: AuctionCreate = Body()):
    check_user(mock_check, token_data)

    if not mock_check and (str(auction.player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    return db.auction_create(auction, mock_check)


# DONE
# AUCTION_DELETE - playerd_id is owner of auction_id
@app.delete("/auctions/{auction_id}", status_code=200)
def player_endpoint(auction_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    check_user(mock_check, token_data)

    if not mock_check and (str(token_data.sub) != db.auction_owner(str(auction_id))):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    db.auction_delete(str(auction_id), mock_check)
    return {"message": f"auction {auction_id} succesfully deleted"}


# DONE
# AUCTION_FILTER - "active":True
@app.get("/auctions/filters", status_code=200)
def player_endpoint(token_data: Annotated[TokenData, Depends(extract_access_token)],
                    auction_filter: AuctionOptional = Query()):
    check_user(mock_check, token_data)

    if auction_filter.active is None or (auction_filter.active is not None and auction_filter.active is False):
        raise HTTPException(status_code=400, detail="Active field must be set to True for player to use this endpoint")

    return db.auction_filter(auction_filter)


##### BID #####


# DONE
# AUCTION_BID - player_id == bid.player_id
@app.post("/auctions/{auction_id}/bids", status_code=201)
def player_endpoint(token_data: Annotated[TokenData, Depends(extract_access_token)],
                    bid: Bid = Body()):
    check_user(mock_check, token_data)
    if not mock_check and (token_data.sub != str(bid.player_id)):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    # extract player id
    return db.bid(bid, mock_check)


# DONE
# BID_FILTER - player_id == bid_filter.player_id
@app.get("/auctions/{player_id}/bid-filter", status_code=200)
def player_endpoint(player_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)],
                    bid_filter: BidOptional = Query()):
    check_user(mock_check, token_data)

    if player_id != bid_filter.player_id or ((not mock_check) and str(player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    # extract player id
    return db.bid_filter(bid_filter)


######### COOPERATION #########

@app.post("/admin/auction/users", status_code=200)
def player_endpoint(token_data: Annotated[TokenData, Depends(extract_access_token)],
                    user: AuthId):
    check_admin(mock_check, token_data)

    db.add_user(user.uid)


@app.delete("/admin/auction/users/{player_id}", status_code=200)
def player_endpoint(token_data: Annotated[TokenData, Depends(extract_access_token)],
                    player_id: str):
    check_admin(mock_check, token_data)

    db.remove_user(player_id)
