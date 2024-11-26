from pydantic import BaseModel

class FreezeTuxModel(BaseModel):
    auction_id: str
    user_id: str
    tux_amount: float
