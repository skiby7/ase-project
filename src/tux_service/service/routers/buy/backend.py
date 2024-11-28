from libs.db import save_tux_transfer, get_fiat_balance

class InsufficientFunds(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def _get_change() -> float:
    return 1.2


def buy_tux(session, user_id: str, tux_amount: float):
    fiat_balance = get_fiat_balance(session, user_id)
    change = _get_change()
    if tux_amount <= 0:
        raise ValueError("Tux amount cannot be lower than or equal to 0!")
    if change*fiat_balance < tux_amount:
        raise InsufficientFunds(f"Your balance is {fiat_balance}, you cannot buy {tux_amount} tux!")
    new_balance = fiat_balance - tux_amount/change
    save_tux_transfer(session, user_id, tux_amount, new_balance)
