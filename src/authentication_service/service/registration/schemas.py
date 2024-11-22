from pydantic import BaseModel

class RegistrationModel(BaseModel):
    username: str
    password: str
    email: str
    
class Account(BaseModel):
    uid: str
    email: str
    username: str
    role: str