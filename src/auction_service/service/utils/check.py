import requests
from auth.access_token_utils import TokenData
from fastapi import HTTPException

def check_user(mock_check: bool, token_data: TokenData):
    if mock_check:
        return True

    if token_data.role != "user":
        return False
    return True

def check_admin(mock_check: bool,token_data: TokenData):
    if mock_check:
        return True

    if token_data.role  != "admin":
        return False

    return True
