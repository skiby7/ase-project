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

def verify_rarity(rarity: str) -> bool: 
    if re.fullmatch(r"[1-5]", rarity):
        return True
    else:
        return False