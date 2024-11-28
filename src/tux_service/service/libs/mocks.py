import os
from logging import getLogger
import random
import sys
from functools import wraps
from routers.transactions.models import PurchaseTransactionModel
from uuid import uuid4
from time import time
logger = getLogger("uvicorn.error")
unix_time = lambda: int(time())
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


def buy_tux_mock(*args, **kwargs):
    pass

def create_purchase_transaction_mock(*args, **kwargs):
    pass


def create_tables_mock(*args, **kwargs):
    pass


def create_user_balance_mock(*args, **kwargs):
    pass


def create_user_transaction_mock(*args, **kwargs):
    pass


def delete_user_account_mock(*args, **kwargs):
    pass


def get_transaction_by_id_mock(*args, **kwargs):
    amount = random.random()*random.randint(0, 1000)
    return PurchaseTransactionModel(
                    transaction_id=str(uuid4()),
                    amount_fiat=amount,
                    amount_tux=amount*1.2,
                    timestamp=unix_time(),
                    user_id=str(uuid4()),
                    filled=random.random() > 0.80)



def get_user_fiat_balance_mock(*args, **kwargs):
    pass


def get_user_transactions_mock(*args, **kwargs):
    pass


def get_user_tux_balance_mock(*args, **kwargs):
    pass


def settle_auction_payments_mock(*args, **kwargs):
    pass


def to_set_mock(*args, **kwargs):
    pass


def transactional_mock(*args, **kwargs):
    pass


def unix_time_mock(*args, **kwargs):
    pass


def update_freezed_tux_mock(*args, **kwargs):
    pass


def update_game_balance_mock(*args, **kwargs):
    pass


def update_user_tux_balance_mock(*args, **kwargs):
    pass


def use_mocks_mock(*args, **kwargs):
    pass


def wraps_mock(*args, **kwargs):
    pass
