from pydantic import BaseModel

class User(BaseModel):
    id: str
    gacha_name: str
    