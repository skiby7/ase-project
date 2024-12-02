import json
import re
import threading
from typing import List
from uuid import uuid4

from .retry_worker import retry_delete_operation, retry_create_operation
from ..login.services import create_admin_access_token
from ..utils.logger import logger
import requests
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from .models import AccountDB
from .schemas import Account
from ..utils import mongo_connection
from ..utils import password_utils
from ..shared_libs.access_token_utils import TokenData

urls_services_to_notify = [
    "https://gacha-roll:9090/notify/user",
    "https://auction:9090/notify/user",
    "https://payment:9090/admin/balances"
]

def initialize_admin():
    with open("/run/secrets/admin_account", "r") as config_file:
        config = json.load(config_file)
        admin_username = config["admin"]["username"]
        admin_password = config["admin"]["password"]
        admin_email = config["admin"]["email"]
    if get_account_by_username(admin_username):
        return
    create_account(admin_email, admin_username, admin_password, 'admin')


def create_account_workflow(email: str, username: str, password: str, role: str) -> Account | None:
    account = create_account(email, username, password, role)
    notify_other_services_new_user(account)
    return account


def notify_other_services_new_user(account: Account) -> None:
    access_token = create_admin_access_token()
    for url in urls_services_to_notify:
        try:
            response = requests.post(url, headers= {"Authorization": f"Bearer {access_token}"},
                                     json=account.model_dump(), timeout=5, verify=False)
            if response.status_code == 200:
                logger.info(f"Success: Notified creation of user {account.uid} to {url}")
            else:
                #eventual consistency
                start_retry_create(url, account.model_dump(), access_token)
        except (requests.RequestException, ConnectionError):
            # eventual consistency
            start_retry_create(url, account.model_dump(), access_token)


def start_retry_create(url, account_dict, access_token: str):
    logger.warning(f"Unexpected error from {url} for user {account_dict}. Retrying...")
    threading.Thread(target=retry_create_operation, args=(url, account_dict, access_token), daemon=True).start()

def create_account(email: str, username: str, password: str, role: str) -> Account:
    validate_input_credentials(email=email, username=username, password=password)
    hashed_password = password_utils.hash_password(password)
    account_db = AccountDB(email=email, uid=str(uuid4()), username=username,
                             hashed_password=hashed_password,
                             role=role)
    accounts_collection = mongo_connection.get_accounts_collection()
    try:
        accounts_collection.insert_one(account_db.model_dump())
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already in use"
        )
    account = Account(uid=account_db.uid, username=account_db.username, email=account_db.email, role=role)
    logger.info(f"Account created: {account}")
    return account

def change_password(uid_account: str, old_pass: str, new_pass: str):
    validate_new_password(new_pass)
    account_DB: Account | None = get_account_db_by_uid(uid_account)
    error_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid uid_account or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    if not account_DB or not password_utils.verify_password(old_pass, account_DB.hashed_password):
        raise error_exception
    save_password_to_db(uid_account, new_pass)


def save_password_to_db(uid_account, new_pass):
    new_hashed_password = password_utils.hash_password(new_pass)
    accounts_collection = mongo_connection.get_accounts_collection()
    update_res = accounts_collection.update_one(
        {"uid": uid_account},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    if update_res.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error in saving updates. Try later"
        )
    logger.info(f"Password for user {uid_account} changed")

def update_account(uid_account: str, email: str | None, username: str | None) -> Account:
    account_DB: Account | None = get_account_db_by_uid(uid_account)
    if not account_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    check_update_param(email, username)
    return save_update_to_db(account_DB, email, username)


def save_update_to_db(account_DB, new_email, new_username) -> Account:
    accounts_collection = mongo_connection.get_accounts_collection()
    update_param = create_update_parm(new_email, new_username)
    try:
        updated_account = accounts_collection.find_one_and_update(
            filter={"uid": account_DB.uid},
            update={"$set": update_param},
            return_document = ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already in use"
        )
    account = Account.from_dict(updated_account)
    logger.info(f"Account updated: {account}")
    return account


def create_update_parm(new_email, new_username):
    update_param = {}
    if new_email:
        update_param["email"] = new_email
    if new_username:
        update_param["username"] = new_username
    return update_param


def check_update_param(email, username):
    if email:
        validate_email(email)
    if username:
        validate_username(username)


def get_account_db_by_uid(uid_account: str) -> AccountDB | None:
    accounts_collection = mongo_connection.get_accounts_collection()
    account_dict = accounts_collection.find_one({"uid": uid_account})
    return AccountDB(**account_dict) if account_dict else None

def get_account_by_uid(uid_account: str) -> Account:
    account_data = get_account_db_by_uid(uid_account)
    if not account_data:
        raise HTTPException(status_code=404, detail="Account not found")
    return Account(uid=account_data.uid, username=account_data.username,
                   email=account_data.email, role=account_data.role)


def get_account_by_username(username: str) -> Account | None:
    accounts_collection = mongo_connection.get_accounts_collection()
    account_dict = accounts_collection.find_one({"username": username})
    return Account.from_dict(account_dict) if account_dict else None


def get_account_by_email(email: str) -> Account | None:
    accounts_collection = mongo_connection.get_accounts_collection()
    account_dict = accounts_collection.find_one({"email": email})
    return Account.from_dict(account_dict) if account_dict else None


def get_all_accounts() -> List[Account]:
    accounts_collection = mongo_connection.get_accounts_collection()
    accounts_docs = list(accounts_collection.find())
    return [Account.from_dict(account_dict) for account_dict in accounts_docs]


def validate_input_credentials(email: str, username: str, password: str):
    validate_email(email)
    validate_username(username)
    validate_new_password(password)


def validate_username(username):
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{2,29}$", username):
        raise HTTPException(status_code=400,
                            detail="Invalid username. It must be 3-30 characters long, start with a letter, and contain only letters, numbers, and underscores.")


def validate_email(email):
    if not re.match(r"^[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(status_code=400, detail="Invalid email format.")


def validate_new_password(password):
    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(
        r"[0-9]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400,
                            detail="Invalid password. Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.")

def delete_account_workflow(uid: str):
    delete_account(uid)
    notify_other_services_delete_user(uid)

def delete_account(uid: str):
    accounts_collection = mongo_connection.get_accounts_collection()
    result = accounts_collection.delete_one({"uid": uid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    logger.info(f"Account {uid} deleted")


def notify_other_services_delete_user(uid: str) -> None:
    access_token = create_admin_access_token()
    for url in urls_services_to_notify:
        try:
            response = requests.delete(f"{url}/{uid}",
                                       headers= {"Authorization": f"Bearer {access_token}"},
                                       timeout=5, verify=False)
            if response.status_code in [200, 404]:
                logger.info(f"Success: Notified deletion of user {uid} to {url}")
            else:
                #eventual consistency
                start_retry_delete(uid, url, access_token)
        except (requests.RequestException, ConnectionError):
            # eventual consistency
            start_retry_delete(uid, url, access_token)


def start_retry_delete(uid, url, access_token: str):
    logger.warning(f"Unexpected error from {url} when deleting user {uid}. Retrying...")
    threading.Thread(target=retry_delete_operation, args=(url, uid, access_token), daemon=True).start()


def can_delete_account(uid_account: str, token_data: TokenData) -> bool:
    return admin_or_sub_account(uid_account, token_data)


def can_update_account(uid_account: str, token_data: TokenData) -> bool:
    return admin_or_sub_account(uid_account, token_data)


def can_change_password_account(uid_account: str, token_data: TokenData) -> bool:
    return admin_or_sub_account(uid_account, token_data)


def can_see_account_info(uid_account: str, token_data: TokenData) -> bool:
    return admin_or_sub_account(uid_account, token_data)


def can_see_all_accounts(token_data: TokenData) -> bool:
    return token_data.role == 'admin'


def admin_or_sub_account(uid_account: str, token_data: TokenData):
    return token_data.role == 'admin' or token_data.sub == uid_account
