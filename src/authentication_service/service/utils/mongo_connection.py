from typing import Annotated
from fastapi import Depends
from pymongo import MongoClient
from pymongo.collection import Collection

mongo_client: MongoClient = None

def startup_db_client(container_name = "db_authentication"):
    global mongo_client
    mongo_client = MongoClient(f"mongodb://{container_name}:27017")

def get_db_client():
    return mongo_client

def get_accounts_collection() -> Collection:
    db = mongo_client["mydatabase"]
    return db["accounts"]

def delete_accounts_collection():
    res = get_accounts_collection().delete_many({})
    print(res)
