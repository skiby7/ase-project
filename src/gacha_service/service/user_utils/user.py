from pydantic import BaseModel

class User(BaseModel):
    uid: str
    gacha_name: str
    