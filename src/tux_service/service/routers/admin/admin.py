from libs.auth import verify
from routers.admin.backend import create_tux_account
from fastapi import APIRouter, HTTPException, Body, Header

from routers.admin.models import TuxAccountModel

router = APIRouter()

@router.post('/management/create_tux_account')
def create(tux_account: TuxAccountModel, Authorization: str = Header()):
    if not verify(Authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        create_tux_account(tux_account)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return {"detail" : "Success!"}
