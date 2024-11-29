from pydantic import BaseModel

class Gacha(BaseModel):
    name: str
    rarity: str
    image: str