from libs.mocks import use_mocks
from logging import getLogger
logger = getLogger("uvicorn.error")

@use_mocks
def verify(token: str) -> bool:
    logger.debug(f"Verifying token {token}")
    return True
