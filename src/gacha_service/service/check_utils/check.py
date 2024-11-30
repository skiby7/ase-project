import requests
from auth.access_token_utils import TokenData

class Checker:

    def tux(mock_check: bool,token_data: TokenData):
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
    
    def user(mock_check: bool,token_data: TokenData):
        if mock_check:
            return True 
        else:
            if token_data.role  == "user":
                return True
            else: 
                return False

    def admin(mock_check: bool,token_data: TokenData):
        if mock_check:
            return True 
        else:
            if token_data.role  == "admin":
                return True
            else: 
                return False