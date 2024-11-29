from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from database.db import database
from typing import Annotated
from auth.access_token_utils import extract_access_token
from auth.access_token_utils import TokenData
from gacha_utils.gacha import Gacha
from check_utils.check import Checker

#TODO: SANITIZE ALL INPUT

mock_check = None
mock_id = None

# token_data: Annotated[TokenData, Depends(extract_access_token)]
# prendere cert

app = FastAPI()
db = database("utils/distros.json")
check = Checker(mock_check)

# View system gacha collection
@app.get("/{id}/gacha/all", status_code=200)
#def user_gacha_all(token_data: Annotated[TokenData, Depends(extract_access_token)]):
def user_gacha_all():
    if check.user():
        return db.get_all_gachas_user()
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View user personal gacha collection
mock_gacha_personal = None
@app.get("/{id}/gacha/collection", status_code=200)
def user_gacha_collection(id: str):
    if not check.user():
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        if mock_gacha_personal:
            res = db.get_user_gacha(1); 
        else: 
            res = db.get_user_gacha(id);
        if res == 1: 
            raise HTTPException(status_code=400, detail="User Not present")
        else: 
            return res

# View Specific Gacha Info
@app.get("/user/gacha/{name}", status_code=200)
def user_gacha_specific(name : str):
    if not check.user():
        raise HTTPException(status_code=400, detail="Invalid User")
    gacha = db.get_specific_gacha(name,mock_id);
    if not gacha: 
        raise HTTPException(status_code=400, detail="Gacha not present")
    else:
        return gacha 

# Use In-Game Currency to Roll Gach
mock_gacha_roll = None
@app.get("/{id}/gacha/roll", status_code=200)
def user_gacha_roll(id: str):
    if not check.user():
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        if check.tux():
            if mock_gacha_roll:
                res = db.get_roll_gacha(1,mock_gacha_roll)
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
def user_gacha_collection():
    if not check.tux():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_all_gachas_admin(mock_id)

# Admin View Specific Gacha
@app.get("/admin/gacha/{name}", status_code=200)
def user_gacha_collection(name: str):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_specific_gacha(name,mock_id)

# Admin add Gacha
@app.post("/admin/gacha", status_code=200)
def user_gacha_modify(gacha: Gacha):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_gacha(gacha.name,gacha.rarity,gacha.image,mock_id)
        if not res: 
            raise HTTPException(status_code=400, detail="Gacha already present")
        return res 

# Admin remove one Gacha 
@app.delete("/admin/gacha/remove/{name}", status_code=200)
def user_gacha_modify(name):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_gacha(name)
        if not res: 
            raise HTTPException(status_code=400, detail="Invalid Name")
        return res 

# Admin Modify Specific Gacha by name 
@app.put("/admin/gacha/", status_code=200)
def user_gacha(gacha: Gacha):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.modify_gacha(gacha.name,gacha.rarity,gacha.image)
        if not res: 
            raise HTTPException(status_code=400, detail="Invalid Name")
        return res 

# Add user
@app.post("/admin/add", status_code=200)
def user_gacha(id):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user(id)
        if not res:
            raise HTTPException(status_code=400, detail="User already Present")
        else: 
            return res

# Delete user
@app.delete("/admin/{id}", status_code=200)
def user_gacha(id: str):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user(id)
        if not res:
            raise HTTPException(status_code=400, detail="User not Present")
        else: 
            return res

# get collection of a user
@app.get("/admin/get/{id}/collection", status_code=200)
def user_gacha(id: str):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        if mock_gacha_personal:
            res = db.get_user_gacha(1); 
        else: 
            res = db.get_user_gacha(id);
        if not res: #TODO: check [] 
            raise HTTPException(status_code=400, detail="User Not present")
        else: 
            return res

# add user gacha
@app.post("/admin/add/gacha", status_code=200)
def user_gacha(user):
    if not check.admin():
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
@app.delete("/admin/{id}/gacha/{name}", status_code=200)
def user_gacha(id, name):
    if not check.admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user_gacha(id,name)
        if not res:
            raise HTTPException(status_code=400, detail="Gacha not Present")
        elif res == 1: 
            raise HTTPException(status_code=400, detail="User doesn't have this gacha")
        elif res == 2: 
            raise HTTPException(status_code=400, detail="User not present")
        else:
            return res