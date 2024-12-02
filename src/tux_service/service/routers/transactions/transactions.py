from libs.auth import verify
from libs.db.db import  get_db, get_user_auction_transactions, get_user_purchase_transactions, get_user_roll_transactions, user_exists
from fastapi import APIRouter, HTTPException, Depends
from libs.access_token_utils import TokenData, extract_access_token
from typing import Annotated

router = APIRouter()

@router.get("/transactions/{user_id}")
def transactions(token_data: Annotated[TokenData, Depends(extract_access_token)], user_id: str, db_session = Depends(get_db)):
    if not verify(token_data, user_id, False):
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
