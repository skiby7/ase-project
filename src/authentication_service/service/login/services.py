import json
from datetime import datetime, timedelta, timezone, UTC
from logging import getLogger
import jwt
from ..registration.schemas import Account
from ..utils import mongo_connection
from ..registration.models import AccountDB
from ..utils import password_utils

logger = getLogger("uvicorn.error")


ISSUER = "auth_ssr_lost_pity"


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

def create_access_token(account: Account, exp: timedelta | None = None, scope: str = "impersonate"):
    to_encode = {
        "iss": ISSUER,
        "sub": account.uid,
        "username": account.username,
        "scope": scope,
        "role": account.role,
        "exp": get_expires(exp)
    }
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm="RS256")
    logger.info(f"Access token created for user {account.username}")
    return encoded_jwt

def create_admin_access_token(exp: timedelta | None = None) -> str:
    with open("/run/secrets/admin_account", "r") as config_file:
        config = json.load(config_file)
        admin_username = config["admin"]["username"]
    account = get_account_by_username(admin_username)
    to_encode = {
        "iss": ISSUER,
        "sub": account.uid,
        "username": account.username,
        "role": account.role,
        "exp": get_expires(timedelta(minutes=60))
    }
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm="RS256")
    logger.info(f"Admin access token created for user {account.username}")
    return encoded_jwt

def get_account_by_username(username: str) -> Account | None:
    accounts_collection = mongo_connection.get_accounts_collection()
    account_dict = accounts_collection.find_one({"username": username})
    return Account.from_dict(account_dict) if account_dict else None


def create_jwt_token(account: Account, exp: timedelta | None = None, aud: str | None = None):
    to_encode = {
        "iss": ISSUER,
        "sub": account.uid,
        "email": account.email,
        "username": account.username,
        "role": account.role,
        "aud": aud or "unknown",
        "iat": datetime.now(UTC),
        "exp": get_expires(exp)
    }
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm="RS256")
    logger.info(f"ID-token created for user {account.username}")
    return encoded_jwt

def get_expires(expires_delta: timedelta | None = None):
    if expires_delta:
        return datetime.now(timezone.utc) + expires_delta
    else:
        return datetime.now(timezone.utc) + timedelta(minutes=15)
