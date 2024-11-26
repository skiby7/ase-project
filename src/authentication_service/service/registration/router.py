from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from . import services
from .schemas import Account, ChangePasswordReq, ModifyAccountReq, RegistrationModel
from ..utils.access_token_utils import extract_access_token
from ..utils.schemas import TokenData

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

admin_router = APIRouter(
    prefix="/admin/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post('/accounts')
def registration(registration_req: RegistrationModel) -> Account:
    account = services.create_account(registration_req.email,
                                      registration_req.username,
                                      registration_req.password,
                                      role='user')
    return account


@router.post('/accounts/{uid_account}/changePassword')
@admin_router.post('/accounts/{uid_account}/changePassword')
def change_password(uid_account: str, change_pass_req: ChangePasswordReq,
                    token_data: Annotated[TokenData, Depends(extract_access_token)]) -> dict:
    if not services.can_change_password_account(uid_account, token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission for the required action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    services.change_password(uid_account,
                             change_pass_req.old_password,
                             change_pass_req.new_password)
    return {"message": "Password successfully updated"}


@admin_router.get('/accounts')
def get_all_accounts(token_data: Annotated[TokenData, Depends(extract_access_token)]) -> dict:
    if not services.can_see_all_accounts(token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission for the required action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    accounts = services.get_all_accounts()
    return {"data": accounts}

@router.get('/accounts/{uid_account}')
@admin_router.get('/accounts/{uid_account}')
def get_account(uid_account: str, token_data: Annotated[TokenData, Depends(extract_access_token)]) -> Account:
    if not services.can_see_account_info(uid_account, token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission for the required action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    account = services.get_account_by_uid(uid_account)
    return account

@router.put('/accounts/{uid_account}')
@admin_router.put('/accounts/{uid_account}')
def modify_account(uid_account: str, modify_account_req: ModifyAccountReq,
                   token_data: Annotated[TokenData, Depends(extract_access_token)]) -> Account:
    if not services.can_update_account(uid_account, token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission for the required action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return services.update_account(uid_account, modify_account_req.email,
                                   modify_account_req.username)


@router.delete('/accounts/{uid_account}')
@admin_router.delete('/accounts/{uid_account}')
def delete_account(uid_account: str, token_data: Annotated[TokenData, Depends(extract_access_token)]) -> dict:
    if not services.can_delete_account(uid_account, token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the permission for the required action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    services.delete_account(uid=uid_account)
    return {"message": f"Account {uid_account} successfully deleted"}
