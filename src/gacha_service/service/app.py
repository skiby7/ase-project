from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from database.db import database
from typing import Annotated
from auth.access_token_utils import extract_access_token
from auth.access_token_utils import TokenData
from gacha_utils.gacha import Gacha
from check_utils.check import check_tux,check_user,check_admin
from user_utils.user import User
from user_utils.add_user import Add_user

mock_check: bool = None
mock_id: bool = None

app = FastAPI()
db = database("utils/distros.json")

# View system gacha collection
@app.get("/user/gacha/all", status_code=200)
def user_gacha_all(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if check_user(mock_check,token_data):
        return db.get_all_gachas_user()
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View user personal gacha collection
@app.get("/{id}/gacha/collection", status_code=200)
def user_gacha_collection(id: str, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_user(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        res = db.get_user_gacha(id);
        if res == 1: 
            raise HTTPException(status_code=400, detail="User Not present")
        else: 
            return res

# View Specific Gacha Info
@app.get("/user/gacha/{name}", status_code=200)
def user_gacha_specific(name: str, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_user(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid User")
    gacha = db.get_specific_gacha(name,mock_id);
    if not gacha: 
        raise HTTPException(status_code=400, detail="Gacha not present")
    else:
        return gacha 

# Use In-Game Currency to Roll Gach
mock_gacha_roll = None
@app.get("/{id}/gacha/roll", status_code=200)
def user_gacha_roll(id: str, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_user(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        if check_tux(mock_check,token_data):
            if mock_gacha_roll:
                res = db.get_roll_gacha(id,mock_gacha_roll)
            else:
                res = db.get_roll_gacha(id,mock_gacha_roll)
            if not res: 
                raise HTTPException(status_code=400, detail="User Not present")
            elif res == 1: 
                raise HTTPException(status_code=400, detail="System ERROR")
            else:
                return res
        else: 
            raise HTTPException(status_code=400, detail="ERROR")

# Admin View Gacha Collection
@app.get("/admin/gacha/all", status_code=200)
def user_gacha_collection(token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_all_gachas_admin(mock_id)

# Admin View Specific Gacha
@app.get("/admin/gacha/{name}", status_code=200)
def user_gacha_collection(name: str, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_specific_gacha(name,mock_id)

# Admin add Gacha
@app.post("/admin/gacha", status_code=200)
def user_gacha_modify(gacha: Gacha, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_gacha(gacha.name,gacha.rarity,gacha.image,mock_id)
        if not res: 
            raise HTTPException(status_code=400, detail="Gacha already present")
        return res 

# Admin remove one Gacha 
@app.delete("/admin/gacha/remove/{name}", status_code=200)
def user_gacha_modify(name, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_gacha(name)
        if not res: 
            raise HTTPException(status_code=400, detail="Gacha Not present")
        return res 

# Admin Modify Specific Gacha by name 
@app.put("/admin/gacha", status_code=200)
def user_gacha(gacha: Gacha, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.modify_gacha(gacha.name,gacha.rarity,gacha.image)
        if not res: 
            raise HTTPException(status_code=400, detail="Gacha Not present")
        return res 

# Add user
@app.post("/admin/users", status_code=200)
def user_gacha(user: Add_user, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user(user.uid)
        if not res:
            raise HTTPException(status_code=400, detail="User already Present")
        else: 
            return res

# Delete user
@app.delete("/admin/users/{id}", status_code=200)
def user_gacha(id: str, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user(id)
        if not res:
            raise HTTPException(status_code=400, detail="User not Present")
        else: 
            return res

# get collection of a user
@app.get("/admin/get/{id}/collection", status_code=200)
def user_gacha(id: str, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.get_user_gacha(id);
        if res == 1:
            raise HTTPException(status_code=400, detail="User Not present")
        else: 
            return res

# add user gacha
@app.post("/admin/add/user/gacha", status_code=200)
def user_gacha(user: User, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user_gacha(user.id,user.gacha_name)
        if not res:
            raise HTTPException(status_code=400, detail="User not Present")
        elif res == 1: 
            raise HTTPException(status_code=400, detail="Gacha not Present")
        else: 
            return res

# delete user gacha
@app.delete("/admin/remove/user/gacha", status_code=200)
def user_gacha(user: User, token_data: Annotated[TokenData, Depends(extract_access_token)]):
    if not check_admin(mock_check,token_data):
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user_gacha(user.id,user.gacha_name)
        if not res:
            raise HTTPException(status_code=400, detail="Gacha not Present")
        elif res == 1: 
            raise HTTPException(status_code=400, detail="User doesn't have this gacha")
        elif res == 2: 
            raise HTTPException(status_code=400, detail="User not present")
        else:
            return res