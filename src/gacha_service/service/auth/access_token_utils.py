from datetime import datetime, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

class TokenData(BaseModel):
    sub: str
    username: str
    role: str
    jwt: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

with open("/run/secrets/jwt_public_key", "r") as f:
    PUBLIC_KEY = f.read()

def extract_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        uid: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        _jwt: str = token
        if uid is None or role is None or is_token_expired(payload):
            raise credentials_exception
        return TokenData(sub=uid, username=username, role=role, jwt=_jwt)
    except jwt.InvalidTokenError:
        raise credentials_exception

def is_token_expired(payload: dict):
    exp = payload["exp"]
    # Validate token expiration
    return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
