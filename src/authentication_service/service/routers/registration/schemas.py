from pydantic import BaseModel

class RegistrationModel(BaseModel):
    username: str
    password: str