import logging

from database.db import database
from uuid import UUID
from fastapi import Body, FastAPI, HTTPException, Depends, Query
import time
from apscheduler.schedulers.background import BackgroundScheduler

from utils.util_classes import AuctionCreate, AuctionStatus, Bid, AuctionOptional, BidOptional, AuthId
from utils.check import check_admin, check_user
from auth.access_token_utils import extract_access_token
from auth.access_token_utils import TokenData
from typing import Annotated

unix_time = lambda: int(time.time())

### INIT ###

mock_check = False


app = FastAPI()
db = database("database/auctions.json", "database/bids.json", "database/users.json")


CHECK_EXPIRY_INTERVAL_MINUTES = 1  # in minute
CHECK_EXPIRY_INTERVAL_SECONDS = 2


def checkAuctionExpiration():
    finishedAuctions = db.checkAuctionExpiration()
    for auction in finishedAuctions:
        auction_id = auction["auction_id"];
        logging.info(f"Handling expired auction {auction_id}")
        db.close_auction(auction, mock_check)


scheduler = BackgroundScheduler()
scheduler.add_job(checkAuctionExpiration, "interval", seconds=CHECK_EXPIRY_INTERVAL_SECONDS, coalesce=False,
                  misfire_grace_time=20)
scheduler.start()




######### ADMIN #########

##### AUCTION #####

@app.post("/admin/auctions", status_code=201)
def admin_auction_create(token_data: Annotated[TokenData, Depends(extract_access_token)], auction: AuctionCreate = Body()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.auction_create(auction, mock_check)


@app.delete("/admin/auctions/{auction_id}", status_code=200)
def admin_auction_delete(auction_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # db.auction_owner(str(auction_id))
    db.auction_delete(str(auction_id), mock_check)
    return {"details":"Success!"}


@app.get("/admin/auctions/{auction_id}", status_code=200)
def admin_auction_info(auction_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")
    auction = db.get_auction_by_id(auction_id)
    del auction["_id"]
    return auction

@app.get("/admin/auctions", status_code=200)
def admin_auction_filter(token_data: Annotated[TokenData, Depends(extract_access_token)], auction_filter: AuctionOptional = Query()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.auction_filter(auction_filter)


##### BID #####


@app.post("/admin/auctions/{auction_id}/bids", status_code=201)
def admin_bid(token_data: Annotated[TokenData, Depends(extract_access_token)], auction_id: UUID, bid: Bid = Body()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.bid(bid, auction_id, mock_check)
    return {"details":"Success!"}


@app.get("/admin/auctions/{auction_id}/bids", status_code=200)
def admin_bid_filter(token_data: Annotated[TokenData, Depends(extract_access_token)], bid_filter: BidOptional = Query()):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.bid_filter(bid_filter)


@app.get("/admin/stats/auctions", status_code=200)
def admin_market_activity(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.market_activity()


@app.post("/admin/auctions/users", status_code=200)
def admin_add_user(token_data: Annotated[TokenData, Depends(extract_access_token)], user: AuthId):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.add_user(user.uid)
    return {"detail":"Success!"}


@app.patch("/admin/auctions/{auction_id}", status_code=200)
def admin_edit_auction_status(auction_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)], status: AuctionStatus = Body() ):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.edit_auction_status(auction_id, status.status)

    return {"detail":"Success!"}


@app.delete("/admin/auctions/users/{player_id}", status_code=200)
def admin_remove_user(token_data: Annotated[TokenData, Depends(extract_access_token)], player_id: str):
    if not check_admin(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.remove_user(player_id)
    return {"detail":"Success!"}

######### PLAYER #########
##### AUCTION #####


@app.post("/auctions", status_code=201)
def create_auction_player(token_data: Annotated[TokenData, Depends(extract_access_token)], auction: AuctionCreate = Body()):
    if not check_user(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not mock_check and (str(auction.player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    return db.auction_create(auction, mock_check)


@app.delete("/auctions/{auction_id}", status_code=200)
def delete_auction_player(auction_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_user(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not mock_check and (str(token_data.sub) != db.auction_owner(str(auction_id))):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    db.auction_delete(str(auction_id), mock_check)
    return {"message": f"auction {auction_id} succesfully deleted"}


@app.get("/auctions", status_code=200)
def get_auctions_player(token_data: Annotated[TokenData, Depends(extract_access_token)], auction_filter: AuctionOptional = Query()):
    if not check_user(mock_check, token_data):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if auction_filter.active is None or (auction_filter.active is not None and auction_filter.active is False):
        raise HTTPException(status_code=400, detail="Active field must be set to True for player to use this endpoint")

    return db.auction_filter(auction_filter)


##### BID #####


@app.post("/auctions/{auction_id}/bids", status_code=201)
def bid_player(token_data: Annotated[TokenData, Depends(extract_access_token)], auction_id: UUID, bid: Bid = Body()):
    check_user(mock_check, token_data)
    if not mock_check and (token_data.sub != str(bid.player_id)):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    return db.bid(bid, auction_id, mock_check)

@app.get("/auctions/{player_id}/bids", status_code=200)
def get_player_bids(player_id: UUID, token_data: Annotated[TokenData, Depends(extract_access_token)], bid_filter: BidOptional = Query()):
    check_user(mock_check, token_data)

    if (not mock_check and str(player_id) != token_data.sub):
        raise HTTPException(status_code=400, detail="Player_id not valid")

    return db.bid_filter(bid_filter)
