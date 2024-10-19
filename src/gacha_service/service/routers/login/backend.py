from random import randint, choice
from hashlib import sha256
from datetime import datetime
import json
import os
import string

from libs.log import INFO, ERROR, DEBUG,  log

def validate_login(username: str, password: str) -> bool:
    # Validation logic
    return True

def get_random_string(length: int) -> str:
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join([choice(letters) for i in range(length)])

def generate_session_token(username) -> dict:
    # maybe use JWT
    token = sha256((get_random_string(10) + datetime.now().strftime('%c')).encode('utf-8')).hexdigest()
    low = randint(0, (len(token) - 1)//2)
    high = low + len(token)//2
    return {
        "username"        : username,
        "token"           : token[low:high],
        "last_connection" : datetime.now().strftime('%c')
    }

def save_session_token(username: str, token: dict):
    pass
    # Save session tokens to the db

def get_session_token(username: str) -> dict:
    # read session tokens from the db
    return {}

def update_last_connection(username: str):
    session_token = get_session_token(username)
    if username not in session_token:
        return
    session_token[username]['last_connection'] = datetime.now().strftime('%c')
    save_session_token(username, session_token)

def is_token_valid(username: str, auth_token: str) -> bool:
    token = get_session_token(username)
    if not token: return False
    if token is None or not is_token_expired(token) or auth_token.lower().replace("Bearer ", "") != token['token']:
        return False
    update_last_connection(username)
    return True

def is_token_expired(token: dict) -> bool:
    return (datetime.now() - datetime.strptime(token['last_connection'], "%c")).total_seconds() // 60 <= 15 # 15 minutes
