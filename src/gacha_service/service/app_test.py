import app as main_app
from auth.access_token_utils import extract_access_token

test = main_app.app

main_app.mock_check = True 
main_app.mock_gacha_roll = True 
main_app.mock_id = True 

async def mock_jwt():
    return {"role": "admin"}

test.dependency_overrides[extract_access_token] = mock_jwt