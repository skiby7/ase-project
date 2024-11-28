from libs.auth import verify
from libs.db.db import get_db, roll_gacha
from fastapi import APIRouter, HTTPException, Body, Header, Depends

from libs.exceptions import InsufficientFunds, UserNotFound
from routers.roll.models import RollModel


router = APIRouter()

@router.post('/roll')
def roll(Authorization: str = Header(), request: RollModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        roll_gacha(db_session, request.user_id)
    except (InsufficientFunds, UserNotFound) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail":"success"}
