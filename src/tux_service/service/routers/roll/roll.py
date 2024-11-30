from libs.auth import verify
from libs.db.db import get_db, roll_gacha, create_roll_transaction
from typing import Annotated
from fastapi import APIRouter, HTTPException, Body, Depends
from libs.access_token_utils import extract_access_token
from libs.access_token_utils import TokenData
from libs.exceptions import InsufficientFunds, UserNotFound
from routers.roll.models import RollModel


router = APIRouter()
ROLL_PRICE = 10

@router.post('/roll')
def roll(token_data: Annotated[TokenData, Depends(extract_access_token)], request: RollModel = Body(), db_session = Depends(get_db)):
    if not verify(token_data, request.user_id, False):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        roll_gacha(db_session, request.user_id, ROLL_PRICE)
    except InsufficientFunds as e:
        new_session = next(get_db())
        create_roll_transaction(new_session, ROLL_PRICE, request.user_id, False)
        raise HTTPException(status_code=400, detail=f"{e}")
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail":"Success!"}

@router.get('/roll/price')
def price():
    return {"price":ROLL_PRICE}
