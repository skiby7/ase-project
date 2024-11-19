from pydantic import BaseModel

class BuyModel(BaseModel):
    amount: float
    user_id: str
