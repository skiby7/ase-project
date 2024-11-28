from libs.auth import verify
from libs.db.db import get_db, buy_tux
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

    try:
        buy_tux(session, buy_request.user_id, buy_request.amount, buy_request.amount/FIAT_TO_TUX)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"{ve}")
    except InsufficientFunds as ins:
        raise HTTPException(status_code=402, detail=f"{ins}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : f"Successully bought {buy_request.amount} tux!"}
