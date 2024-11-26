from libs.auth import verify
from libs.db.db import get_db, get_user_fiat_balance, get_user_tux_balance
from fastapi import APIRouter, HTTPException, Body, Header, Depends


router = APIRouter()

@router.post('/pay')
def pay(user_id: str, Authorization: str = Header()):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
