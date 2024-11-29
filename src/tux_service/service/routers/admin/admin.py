from libs.auth import verify
from fastapi import APIRouter, HTTPException, Body, Header, Depends
from routers.admin.models import TuxAccountModel
from libs.db.db import create_user_balance, delete_user_balance, get_db, get_highest_bidder, update_freezed_tux, settle_auction_payments
from routers.admin.models import FreezeTuxModel, SettleAuctionModel
from libs.exceptions import AlreadySettled, AuctionNotFound, UserNotFound, InsufficientFunds

router = APIRouter()

@router.post('/admin/balances/create')
def create( Authorization: str = Header(), tux_account: TuxAccountModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        create_user_balance(db_session, tux_account.initial_fiat_amount, tux_account.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : "Success!"}

@router.delete('/admin/balances/{user_id}/delete')
def delete(user_id: str, Authorization: str = Header(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        delete_user_balance(db_session, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {"detail" : "Success!"}


@router.post("/admin/auctions/{auction_id}/freeze")
def freeze(auction_id: str, Authorization: str = Header(), request: FreezeTuxModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        update_freezed_tux(db_session, auction_id, request.user_id, request.tux_amount)
    except (InsufficientFunds, AlreadySettled, UserNotFound, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"details" : "success"}


@router.post("/admin/auctions/{auction_id}/settle-auction")
def settle(auction_id: str, Authorization: str = Header(), request: SettleAuctionModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        settle_auction_payments(db_session, auction_id, request.winner_id, request.auctioneer_id)
    except (InsufficientFunds, AlreadySettled, UserNotFound, AuctionNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")



@router.get("/admin/auctions/{auction_id}")
def highest_bidder(auction_id: str, Authorization: str = Header(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        get_highest_bidder(db_session, auction_id)
    except (AuctionNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
