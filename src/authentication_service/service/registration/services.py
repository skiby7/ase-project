from fastapi import HTTPException
from passlib.context import CryptContext
from .models import AccountDB
from .schemas import Account
from pymongo import MongoClient
from uuid import uuid4

client = MongoClient("db_authentication", 27017, maxPoolSize=50)
db = client["mydatabase"]
accounts_collection = db["accounts"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_account(username: str, password: str) -> Account:
    if accounts_collection.find_one({"username": username}):
        raise HTTPException(status_code=409, detail="Username already in use")
    hashed_password = hash_password(password)
    account_data = AccountDB(uid = str(uuid4()), username = username, hashed_password = hashed_password)
    accounts_collection.insert_one(account_data.model_dump())
    return Account(uid = account_data.uid, username = account_data.username)

def delete_account(uid: str):
    account = accounts_collection.find_one({"uid": uid})
    if not account:
        raise HTTPException(status_code=404, detail="No account found with that identifier")
    result = accounts_collection.delete_one({"uid": uid})
    if result.deleted_count == 1:
        print(f"Account with UID '{uid}' successfully deleted.")
    else:
        raise HTTPException(status_code=500, detail="Error in deleting account")


def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
