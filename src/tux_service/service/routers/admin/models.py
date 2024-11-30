from pydantic import BaseModel

class TuxAccountModel(BaseModel):
    user_id: str
    initial_fiat_amount: float

class FreezeTuxModel(BaseModel):
    user_id: str
    tux_amount: float

class SettleAuctionModel(BaseModel):
    winner_id: str
    auctioneer_id: str
