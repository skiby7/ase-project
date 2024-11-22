import re
from typing import Annotated
from pymongo.collection import Collection
from fastapi import Depends, HTTPException

from ..utils.schemas import TokenData
from ..utils import mongo_connection
from .models import AccountDB
from .schemas import Account
from ..utils import password_utils
from uuid import uuid4

def create_account(email: str, username: str, password: str, role: str) -> Account:
    validate_input_credentials(email=email, username=username, password=password)
    accounts_collection = mongo_connection.get_accounts_collection()
    if accounts_collection.find_one({"username": username}):
        raise HTTPException(status_code=409, detail="Username already in use")
    hashed_password = password_utils.hash_password(password)
    account_data = AccountDB(email = email, uid = str(uuid4()), username = username, hashed_password = hashed_password, role=role)
    accounts_collection.insert_one(account_data.model_dump())
    return Account(uid = account_data.uid, username = account_data.username, 
                   email = account_data.email, role = role)

def validate_input_credentials(email: str, username: str, password: str):
    if not re.match(r"^[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(status_code=404, detail="Invalid email format.")

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{2,29}$", username):
        raise HTTPException(status_code=404, detail="Invalid username. It must be 3-30 characters long, start with a letter, and contain only letters, numbers, and underscores.")

    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=404, detail="Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.")
    
def delete_account(uid: str):
    accounts_collection = mongo_connection.get_accounts_collection()
    account = accounts_collection.find_one({"uid": uid})
    if not account:
        raise HTTPException(status_code=404, detail="No account found with that identifier")
    result = accounts_collection.delete_one({"uid": uid})
    if result.deleted_count != 1:
        raise HTTPException(status_code=500, detail="Error in deleting account")


def can_delete_account(uid_account: str, token_data: TokenData) -> bool:
    return admin_or_sub_account(uid_account, token_data)

def admin_or_sub_account(uid_account: str, token_data: TokenData):
    return token_data.role == 'admin' or token_data.sub == uid_account