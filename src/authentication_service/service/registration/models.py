from pydantic import BaseModel

class AccountDB(BaseModel):
    uid: str
    email: str
    username: str
    hashed_password: str
    role: str
    