from datetime import datetime, timedelta, timezone
from logging import getLogger
import jwt
from ..registration.schemas import Account
from ..utils import mongo_connection
from ..registration.models import AccountDB
from ..utils import password_utils

logger = getLogger("uvicorn.error")

with open("/run/secrets/jwt_private_key", "r") as f:
    PRIVATE_KEY = f.read()

def validate_login(username: str, password: str) -> Account | None:
    accounts_collection = mongo_connection.get_accounts_collection()
    account_dict = accounts_collection.find_one({"username": username})
    if not account_dict:
        return None
    account_DB = AccountDB(**account_dict)
    if not password_utils.verify_password(password, account_DB.hashed_password):
        return None
    return Account(uid=account_DB.uid, email=account_DB.email, username=account_DB.username, role=account_DB.role)

def get_account_info(uid_account: str) -> Account | None:
    accounts_collection = mongo_connection.get_accounts_collection()
    account_dict = accounts_collection.find_one({"uid": uid_account})
    if not account_dict:
        return None
    account_DB = AccountDB(**account_dict)
    return Account(uid=account_DB.uid,
                   email=account_DB.email,
                   username=account_DB.username,
                   role=account_DB.role)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode.update({"exp": get_expires(expires_delta)})
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm="RS256")
    return encoded_jwt

def get_expires(expires_delta: timedelta | None = None):
    if expires_delta:
        return datetime.now(timezone.utc) + expires_delta
    else:
        return datetime.now(timezone.utc) + timedelta(minutes=15)
