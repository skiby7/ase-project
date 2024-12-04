import requests
from auth.access_token_utils import TokenData
from fastapi import HTTPException

def check_tux(mock_check: bool,token_data: TokenData):
    if mock_check:
        return True
    else:
        headers = {
            "Authorization": f"Bearer {token_data.jwt}",
            "Content-Type": "application/json"
        }
        data = {
            "user_id": str(token_data.sub),
        }
        try:
            response = requests.post("https://tux_service:9290/roll", json=data, headers=headers, verify=False)
            if not response.status_code == 200:
                return False
            else:
                return True
        except (requests.RequestException, ConnectionError):
            raise HTTPException(status_code=400, detail="Internal Server Error")

def check_user(mock_check: bool,token_data: TokenData, id: str):
    if mock_check:
        return True
    else:
        if id is not None:
            if token_data.sub != id:
                return False
        if token_data.role == "user":
            return True
        else:
            return False

def check_admin(mock_check: bool,token_data: TokenData):
    if mock_check:
        return True
    else:
        if token_data.role == "admin":
            return True
        else:
            return False
