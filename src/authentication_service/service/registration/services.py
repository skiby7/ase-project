import json
import re
from typing import List
from uuid import uuid4

from fastapi import HTTPException, status

from .models import AccountDB
from .schemas import Account
from ..utils import mongo_connection
from ..utils import password_utils
from ..utils.schemas import TokenData

urls_services_to_notify = [
    ""
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
    notify_other_services_new_user()
    return account

def notify_other_services_new_user():
    return


def create_account(email: str, username: str, password: str, role: str) -> Account:
    validate_input_credentials(email=email, username=username, password=password)
    check_if_param_already_in_use(email, username)
    hashed_password = password_utils.hash_password(password)
    account_data = AccountDB(email=email, uid=str(uuid4()), username=username, hashed_password=hashed_password,
                             role=role)
    accounts_collection = mongo_connection.get_accounts_collection()
    accounts_collection.insert_one(account_data.model_dump())
    return Account(uid=account_data.uid, username=account_data.username,
                   email=account_data.email, role=role)


def change_password(uid_account: str, old_pass: str, new_pass: str):
    validate_password(new_pass)
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


def check_if_param_already_in_use(email, username):
    if get_account_by_username(username):
        raise HTTPException(status_code=409, detail="Username already in use")
    if get_account_by_email(email):
        raise HTTPException(status_code=409, detail="Email already in use")


def update_account(uid_account: str, email: str | None, username: str | None) -> Account:
    account_DB: Account | None = get_account_db_by_uid(uid_account)
    if not account_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    check_update_param(email, username)
    check_if_param_already_in_use(email, username)
    save_update_to_db(account_DB, email, username)
    return get_account_by_uid(uid_account)


def save_update_to_db(account_DB, new_email, new_username):
    accounts_collection = mongo_connection.get_accounts_collection()
    update_res = accounts_collection.update_one(
        {"uid": account_DB.uid},
        {"$set": {
            "email": new_email or account_DB.email,
            "username": new_username or account_DB.username}
        }
    )
    if update_res.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error in saving updates. Try later"
        )


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
    validate_password(password)


def validate_username(username):
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{2,29}$", username):
        raise HTTPException(status_code=400,
                            detail="Invalid username. It must be 3-30 characters long, start with a letter, and contain only letters, numbers, and underscores.")


def validate_email(email):
    if not re.match(r"^[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(status_code=400, detail="Invalid email format.")


def validate_password(password):
    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(
        r"[0-9]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400,
                            detail="Invalid password. Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.")


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
