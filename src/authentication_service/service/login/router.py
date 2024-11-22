from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..utils.access_token_utils import extract_access_token
from ..utils.schemas import TokenData
from . import services

router = APIRouter()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post('/token')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = services.validate_login(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = services.create_access_token(
        data = {"sub": user.uid, "username": user.username,"role": user.role}, 
        expires_delta=timedelta(minutes=15)
    )
    return {"access_token" : access_token, "token_type": "bearer"}


@router.get('/userinfo')
def verify(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    account = services.get_account_info(uid_account=token_data.sub)
    if account == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return account
