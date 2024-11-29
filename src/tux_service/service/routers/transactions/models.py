from pydantic import BaseModel

class PurchaseTransactionModel(BaseModel):
    amount_fiat: float
    amount_tux: float
    purchased_tux: float
    timestamp: int
    user_id: str
    filled: bool
    transaction_id: str

class AuctionTransactionModel(BaseModel):
    transaction_id: str
    auction_id: str
    amount_tux: float
    timestamp: int
    from_user_id: str
    to_user_id: str

class RollTransactionModel(BaseModel):
    transaction_id: str
    amount_tux: float
    timestamp: int
    user_id: str
    filled: bool
