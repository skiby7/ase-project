from typing import Annotated
from libs.auth import verify
from fastapi import APIRouter, HTTPException, Body, Depends
from routers.admin.models import TuxAccountModel
from libs.db.db import create_user_balance, delete_user_balance, get_db, get_highest_bidder, update_freezed_tux, settle_auction_payments
from libs.access_token_utils import TokenData, extract_access_token
from routers.admin.models import FreezeTuxModel, SettleAuctionModel
from libs.exceptions import AlreadySettled, AuctionNotFound, UserNotFound, InsufficientFunds

router = APIRouter()

@router.post('/admin/balances/create')
def create(token_data: Annotated[TokenData, Depends(extract_access_token)], tux_account: TuxAccountModel = Body(), db_session = Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        create_user_balance(db_session, tux_account.initial_fiat_amount, tux_account.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : "Success!"}

@router.delete('/admin/balances/{user_id}/delete')
def delete(user_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], db_session = Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        delete_user_balance(db_session, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {"detail" : "Success!"}


@router.post("/admin/auctions/{auction_id}/freeze")
def freeze(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], request: FreezeTuxModel = Body(), db_session = Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        update_freezed_tux(db_session, auction_id, request.user_id, request.tux_amount)
    except (InsufficientFunds, AlreadySettled, UserNotFound, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : "Success!"}


@router.post("/admin/auctions/{auction_id}/settle-auction")
def settle(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], request: SettleAuctionModel = Body(), db_session = Depends(get_db)):
    if not verify(token_data, None, False):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        settle_auction_payments(db_session, auction_id, request.winner_id, request.auctioneer_id)
    except (InsufficientFunds, AlreadySettled, UserNotFound, AuctionNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : "Success!"}


@router.get("/admin/auctions/{auction_id}/highest-bidder")
def highest_bidder(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], db_session = Depends(get_db)):
    if not verify(token_data, None, False):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_id, amount = get_highest_bidder(db_session, auction_id)
    except (AuctionNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {
        "user_id" : user_id,
        "tux_amount" : amount
    }