import os
from logging import getLogger
import sys
from functools import wraps
logger = getLogger("uvicorn.error")

class MockSession:
    def open(self):
        pass
    def close(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass


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

def verify_mock(token: str) -> bool:
    logger.debug(f"MOCK -> Verifying token {token}")
    return True

def get_fiat_balance_mock(session, user_id):
    return 10000.0

def get_tux_balance_mock(session, user_id):
    return 10000.0
