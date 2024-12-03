from pydantic import BaseModel
import re

class Gacha(BaseModel):
    name: str
    rarity: str
    image: str

def verify_name(name: str) -> bool: 
    if len(name) > 30:
        return False

    if re.fullmatch(r"[a-zA-Z!?_]*", name):
        return True
    else:
        return False