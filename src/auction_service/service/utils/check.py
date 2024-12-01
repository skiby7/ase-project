import requests
from auth.access_token_utils import TokenData
from fastapi import HTTPException
'''
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
        response = requests.post("https://127.0.0.1:9390/roll", json=data, headers=headers)
        if not response.status_code == 200:
            return False
        else: 
            return True
'''

def check_user(mock_check: bool,token_data: TokenData):
    if not mock_check:
        if token_data.role  != "user":
            raise HTTPException(status_code=400, detail="Invalid User")

def check_admin(mock_check: bool,token_data: TokenData):
    if not mock_check:
        if token_data.role  != "admin":
            raise HTTPException(status_code=400, detail="Invalid User")

