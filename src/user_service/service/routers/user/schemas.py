from pydantic import BaseModel

class UserModel(BaseModel):
    id: str
    username: str
    image_uri: str
