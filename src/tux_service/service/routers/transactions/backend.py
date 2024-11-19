from libs.db import get_transactions
from routers.transactions.models import TransactionModel

def get_transaction_history(user_id: str) -> list[TransactionModel]:
    transactions = get_transactions(user_id, -1, -1)
    return transactions
