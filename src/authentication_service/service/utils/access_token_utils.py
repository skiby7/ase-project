

from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .schemas import TokenData

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
        if uid is None or role is None or is_token_expired(payload):
            raise credentials_exception
        return TokenData(sub=uid, username=username, role=role)
    except jwt.InvalidTokenError:
        raise credentials_exception

def is_token_expired(payload: dict):
    exp = payload["exp"]
    # Validate token expiration
    return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
