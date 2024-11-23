from libs.auth import verify
from libs.db import Session, get_db
from fastapi import APIRouter, HTTPException, Body, Header, Depends
from routers.transactions.backend import get_transaction_history

router = APIRouter()

@router.get("/transactions/{user_id}")
def transactions(user_id: str, Authorization: str = Header(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    transactions = get_transaction_history(db_session, user_id)
