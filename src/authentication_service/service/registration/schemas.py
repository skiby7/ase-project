from pydantic import BaseModel

class RegistrationModel(BaseModel):
    username: str
    password: str
    
class Account(BaseModel):
    uid: str
    username: str