from pydantic import BaseModel

class RegistrationModel(BaseModel):
    username: str
    password: str
    email: str

class ModifyAccountReq(BaseModel):
    username: str | None = None
    email: str | None = None

class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

class Account(BaseModel):
    uid: str
    email: str
    username: str
    role: str

    @staticmethod
    def from_dict(account_dict):
        return Account(uid=account_dict["uid"], username=account_dict["username"],
                       email=account_dict.get("email", ""), role=account_dict["role"])
