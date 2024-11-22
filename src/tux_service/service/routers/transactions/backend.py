from libs.db import get_user_transactions
from routers.transactions.models import TransactionModel

def get_transaction_history(session, user_id: str) -> list[TransactionModel]:
    transactions = get_user_transactions(session, user_id)
    return transactions
