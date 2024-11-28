from pydantic import BaseModel

class TuxAccountModel(BaseModel):
    user_id: str
    initial_fiat_amount: float
