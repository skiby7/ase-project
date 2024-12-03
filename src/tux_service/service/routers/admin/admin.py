from typing import Annotated
from libs.auth import verify
from fastapi import APIRouter, HTTPException, Body, Depends
from routers.admin.models import TuxAccountModel
from libs.db.db import create_user_balance, delete_user_balance, user_exists, get_user_auction_transactions, get_user_purchase_transactions, get_user_roll_transactions, get_db, get_highest_bidder, update_freezed_tux, settle_auction_payments, delete_auction
from libs.access_token_utils import TokenData, extract_access_token
from routers.admin.models import FreezeTuxModel, SettleAuctionModel
from libs.exceptions import AlreadySettled, AuctionNotFound, UserNotFound, InsufficientFunds

router = APIRouter()


@router.post('/admin/balances')
def create(token_data: Annotated[TokenData, Depends(extract_access_token)], tux_account: TuxAccountModel = Body(), db_session=Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        create_user_balance(db_session, tux_account.initial_fiat_amount, tux_account.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail": "Success!"}


@router.delete('/admin/balances/{user_id}')
def delete(user_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], db_session=Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        delete_user_balance(db_session, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {"detail": "Success!"}


@router.post("/admin/auctions/{auction_id}/freeze")
def freeze(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], request: FreezeTuxModel = Body(), db_session=Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        update_freezed_tux(db_session, auction_id,
                           request.user_id, request.tux_amount)
    except (AlreadySettled, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except InsufficientFunds as e:
        raise HTTPException(status_code=402, detail=f"{e}")
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail": "Success!"}

@router.delete("/admin/auctions/{auction_id}")
def auction_delete(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], db_session = Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        delete_auction(db_session, auction_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail": "Success!"}

@router.post("/admin/auctions/{auction_id}/settle-auction")
def settle(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], request: SettleAuctionModel = Body(), db_session=Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        settle_auction_payments(db_session, auction_id,
                                request.winner_id, request.auctioneer_id)
    except (AlreadySettled, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except InsufficientFunds as e:
        raise HTTPException(status_code=402, detail=f"{e}")
    except (UserNotFound, AuctionNotFound) as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail": "Success!"}



@router.get("/admin/transactions/{user_id}")
def transactions(token_data: Annotated[TokenData, Depends(extract_access_token)], user_id: str, db_session = Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user_exists(db_session, user_id):
        raise HTTPException(status_code=404, detail="User does not exists!")
    purchase = get_user_purchase_transactions(db_session, user_id)
    auction = get_user_auction_transactions(db_session, user_id)
    roll = get_user_roll_transactions(db_session, user_id)
    return {
        "purchase" : purchase,
        "auction"  : auction,
        "roll"    : roll
    }

@router.get("/admin/auctions/{auction_id}/highest-bidder")
def highest_bidder(auction_id: str, token_data: Annotated[TokenData, Depends(extract_access_token)], db_session=Depends(get_db)):
    if not verify(token_data, None, True):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_id, amount = get_highest_bidder(db_session, auction_id)
    except AuctionNotFound as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {
        "user_id": user_id,
        "tux_amount": amount
    }
