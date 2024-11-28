from pydantic import BaseModel

class FreezeTuxModel(BaseModel):
    auction_id: str
    user_id: str
    tux_amount: float

class SettleAuctionModel(BaseModel):
    auction_id: str
    winner_id: str
    auctioneer_id: str
