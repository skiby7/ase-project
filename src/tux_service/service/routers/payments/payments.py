from libs.auth import verify
from routers.payments.backend import get_tux_balance
from fastapi import APIRouter, HTTPException, Body, Header

router = APIRouter()

@router.post('/balance/{user_ud}')
def buy(user_id: str, Authorization: str = Header()):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        balance = get_tux_balance(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {"balance" : balance}
