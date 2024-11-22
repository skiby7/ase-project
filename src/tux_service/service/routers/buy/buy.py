from libs.auth import verify
from routers.buy.models import BuyModel
from routers.buy.backend import InsufficientFunds, buy_tux
from fastapi import APIRouter, HTTPException, Body, Header

router = APIRouter()

@router.post('/buy')
def buy(Authorization: str = Header(), buy_request: BuyModel = Body()):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        buy_tux(buy_request.user_id, buy_request.amount)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"{ve}")
    except InsufficientFunds as ins:
        raise HTTPException(status_code=402, detail=f"{ins}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : f"Successully bought {buy_request.amount} tux!"}
