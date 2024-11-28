from libs.auth import verify
from libs.exceptions import UserNotFound, AlreadySettled, InsufficientFunds
from libs.db.db import get_db, settle_auction_payments, update_freezed_tux, get_user_tux_balance, get_user_fiat_balance
from fastapi import APIRouter, HTTPException, Body, Header, Depends

from routers.balances.models import FreezeTuxModel, SettleAuctionModel


router = APIRouter()


@router.get("/balances/{user_id}")
def balance(user_id: str, Authorization: str = Header(), session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        tux_balance = get_user_tux_balance(session, user_id)
        fiat_balance = get_user_fiat_balance(session, user_id)
    except UserNotFound as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {
        "fiat_balance" : fiat_balance,
        "tux_balance"  : tux_balance
    }

@router.post("/balances/{user_id}/freeze")
def freeze(user_id: str, Authorization: str = Header(), request: FreezeTuxModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        update_freezed_tux(db_session, request.auction_id, request.user_id, request.tux_amount)
    except (InsufficientFunds, AlreadySettled, UserNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"details" : "success"}

@router.post("/balances/settle-auction")
def settle(Authorization: str = Header(), request: SettleAuctionModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        settle_auction_payments(db_session, request.auction_id, request.winner_id, request.auctioneer_id)
    except (InsufficientFunds, AlreadySettled, UserNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
