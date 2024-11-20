from fastapi import APIRouter, HTTPException, Body, Header

from .schemas import LoginModel

router = APIRouter()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post('/login')
def login(login_info: LoginModel = Body()):

    if lb.validate_login(login_info.username, login_info.password):
        raise HTTPException(status_code=403, detail="Not authorized")

    token = lb.generate_session_token(login_info.username)
    lb.save_session_token(login_info.username, token)
    return {"token" : token}

@router.get('/login/verify/{username}')
def verify(username: str, Authorization: str = Header()):
       return {"token" : lb.is_token_valid(username, Authorization)}
