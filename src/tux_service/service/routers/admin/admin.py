from libs.auth import verify
from fastapi import APIRouter, HTTPException, Body, Header, Depends
from routers.admin.models import TuxAccountModel
from libs.db.db import create_user_balance, delete_user_balance, get_db

router = APIRouter()

@router.post('/management/tux-accounts/create')
def create( Authorization: str = Header(), tux_account: TuxAccountModel = Body(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        create_user_balance(db_session, tux_account.initial_fiat_amount, tux_account.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return {"detail" : "Success!"}

@router.delete('/management/tux-accounts/{user_id}/delete')
def delete(user_id: str, Authorization: str = Header(), db_session = Depends(get_db)):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        delete_user_balance(db_session, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {"detail" : "Success!"}
