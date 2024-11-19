from libs.auth import verify
from fastapi import APIRouter, HTTPException, Body, Header
from tux_service.service.routers.transactions.backend import get_transaction_history

router = APIRouter()

@router.get("/transactions/{user_id}")
def transactions(user_id: str, Authorization: str = Header()):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    transactions = get_transaction_history(user_id)
