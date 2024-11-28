
class InsufficientTux(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def get_tux_balance(sesison, user_id: str) -> float:
    return 10.0
