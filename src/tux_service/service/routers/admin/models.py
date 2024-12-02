from pydantic import BaseModel, Field


class TuxAccountModel(BaseModel):
    user_id: str = Field(alias="uid")
    initial_fiat_amount: float = 1000

class FreezeTuxModel(BaseModel):
    user_id: str
    tux_amount: float

class SettleAuctionModel(BaseModel):
    winner_id: str
    auctioneer_id: str
