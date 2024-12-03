from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from . import services
from ..shared_libs.access_token_utils import extract_access_token
from ..shared_libs.access_token_utils import TokenData

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


@router.post('/token')
@admin_router.post('/token')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    account = services.validate_login(form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = services.create_access_token(
        account=account,
        exp=timedelta(minutes=15)
    )
    response = {"access_token": access_token, "token_type": "bearer"}
    if 'openid' in form_data.scopes:
        id_token = services.create_jwt_token(
            account=account,
            exp=timedelta(minutes=15),
            aud=form_data.client_id
        )
        response.update({"id_token": id_token})
    return response


@router.get('/userinfo')
@admin_router.get('/userinfo')
def verify(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    account = services.get_account_info(uid_account=token_data.sub)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return account
