from libs.auth import verify
from libs.db.db import get_db, buy_tux, create_purchase_transaction, get_user_tux_balance, get_user_fiat_balance
from routers.buy.models import BuyModel
from fastapi import APIRouter, HTTPException, Body, Header, Depends
from logging import getLogger

from libs.exceptions import InsufficientFunds
logger = getLogger("uvicorn.error")
router = APIRouter()

FIAT_TO_TUX = 1.2


@router.post('/buy')
def buy(Authorization: str = Header(), buy_request: BuyModel = Body(), session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    tux_amount = buy_request.amount/FIAT_TO_TUX
    try:
        buy_tux(session, buy_request.user_id, buy_request.amount, tux_amount)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"{ve}")
    except InsufficientFunds as ins:
        new_session = next(get_db())
        tux_balance = get_user_tux_balance(session, buy_request.user_id)
        fiat_balance = get_user_fiat_balance(session, buy_request.user_id)
        create_purchase_transaction(new_session, tux_amount, fiat_balance, tux_balance, buy_request.user_id, False)
        raise HTTPException(status_code=402, detail=f"{ins}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : f"Successully bought {buy_request.amount} tux!"}


@router.get("/tux-price")
def tux_price():

    return {"price" : FIAT_TO_TUX}
