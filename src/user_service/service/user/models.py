from pydantic import BaseModel

class UserDB(BaseModel):
    uid: str
    first_name: str | None
    last_name: str | None
    user_image: str | None
    date_of_birth: str | None