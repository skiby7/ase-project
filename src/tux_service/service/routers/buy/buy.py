from libs.auth import verify
from libs.db import get_db
from routers.buy.models import BuyModel
from routers.buy.backend import InsufficientFunds, buy_tux
from fastapi import APIRouter, HTTPException, Body, Header, Depends
from logging import getLogger
logger = getLogger("uvicorn.error")
router = APIRouter()

@router.post('/buy')
def buy(Authorization: str = Header(), buy_request: BuyModel = Body(), session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        buy_tux(session, buy_request.user_id, buy_request.amount)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"{ve}")
    except InsufficientFunds as ins:
        raise HTTPException(status_code=402, detail=f"{ins}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : f"Successully bought {buy_request.amount} tux!"}
