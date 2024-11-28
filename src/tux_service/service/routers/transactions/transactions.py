from libs.auth import verify
from libs.db.db import  get_db, get_user_auction_transactions, get_user_purchase_transactions, user_exists
from fastapi import APIRouter, HTTPException, Header, Depends

router = APIRouter()

@router.get("/transactions/{user_id}")
def transactions(user_id: str, Authorization: str = Header(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user_exists(db_session, user_id):
        raise HTTPException(status_code=404, detail="User does not exists!")
    purchase = get_user_purchase_transactions(db_session, user_id)
    auction = get_user_auction_transactions(db_session, user_id)
    return {
        "purchase" : purchase,
        "auction"  : auction
    }
