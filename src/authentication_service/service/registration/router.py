from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import Account, RegistrationModel
from . import services
from ..utils.access_token_utils import extract_access_token
from ..utils.schemas import TokenData


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post('/account')
def registration(registration_req: RegistrationModel) -> Account:
    account = services.create_account(registration_req.email, 
                             registration_req.username, 
                             registration_req.password,
                             role = 'user')
    return account

@router.post('/admin/account')
def registration(registration_req: RegistrationModel) -> Account:
    account = services.create_account(registration_req.email, 
                             registration_req.username, 
                             registration_req.password,
                             role = 'admin')
    return account

@router.delete('/account/{uid_account}')
def delete_account(uid_account: str, token_data: Annotated[TokenData, Depends(extract_access_token)]) -> dict:
    if(not services.can_delete_account(uid_account, token_data)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission for the required action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    services.delete_account(uid = uid_account)
    return {"message": f"Account {uid_account} successfully deleted"}

