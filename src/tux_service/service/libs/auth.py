from libs.mocks import use_mocks
from logging import getLogger
from libs.access_token_utils import TokenData
from typing import Optional
logger = getLogger("uvicorn.error")

@use_mocks
def verify(token: TokenData, user_id: Optional[str], admin: bool) -> bool:
    logger.debug(f"Verifying token for {token.username}")
    role_is_admin = token.role == 'admin'
    if admin:
        return role_is_admin
    return token.sub == user_id
