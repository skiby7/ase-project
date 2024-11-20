from pydantic import BaseModel

class AccountDB(BaseModel):
    uid: str
    username: str
    hashed_password: str
    