from libs.db import get_transactions, save_transaction

class InsufficientFunds(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def _get_change() -> float:
    return 1.2

def get_fiat_balance(user_id: str) -> float:
    return 10.0

def buy_tux(user_id: str, tux_amount: float):
    fiat_balance = get_fiat_balance(user_id)
    change = _get_change()
    if tux_amount <= 0:
        ValueError(f"Tux amount cannot be lower or equal than 0!")
    if change*fiat_balance < tux_amount:
        raise InsufficientFunds(f"Your balance is {fiat_balance}, you cannot buy {tux_amount} tux!")
    save_transaction(user_id, tux_amount)
