from libs.auth import verify
from libs.db.db import get_db, get_user_fiat_balance, get_user_tux_balance
from fastapi import APIRouter, HTTPException, Body, Header, Depends


router = APIRouter()

@router.get('/balances/{user_id}')
def balance(user_id: str, Authorization: str = Header(), session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        tux_balance = get_user_tux_balance(session, user_id)
        fiat_balance = get_user_fiat_balance(session, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {
        "fiat_balance" : fiat_balance,
        "tux_balance"  : tux_balance
    }

@router.post('/pay')
def pay(user_id: str, Authorization: str = Header()):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
