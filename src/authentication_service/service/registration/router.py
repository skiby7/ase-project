from fastapi import APIRouter, HTTPException, Body, Header

from .schemas import Account, RegistrationModel
from .services import create_account , delete_account

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post('/account')
def registration(registration_req: RegistrationModel) -> Account:
    account = create_account(registration_req.username, registration_req.password)
    return account

@router.delete('/account/{uid_account}')
def rest_delete_account(uid_account: str) -> None:
    delete_account(uid = uid_account)