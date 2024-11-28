from pydantic import BaseModel

class Gacha(BaseModel):
    name: int
    rarity: str
    image: str