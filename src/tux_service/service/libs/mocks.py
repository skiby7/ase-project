import os
from logging import getLogger
import sys
from functools import wraps
from time import time
logger = getLogger("uvicorn.error")
unix_time = lambda: int(time())


def use_mocks(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.getenv("TEST_RUN", "false").lower() == "true":
            mock_func = getattr(sys.modules["libs.mocks"], f"{func.__name__}_mock", default_mock)
            return mock_func(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper


def default_mock(*args, **kwargs):
    pass


def verify_mock(*args, **kwargs) -> bool:
    logger.debug("MOCKING AUTH")
    return True
