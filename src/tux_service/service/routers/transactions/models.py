from pydantic import BaseModel

class TransactionModel(BaseModel):
    amount_fiat: float
    amount_tux: float
    timestamp: int
    user_id: str
    filled: bool
    transaction_id: str
