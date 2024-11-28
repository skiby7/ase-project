from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from database.db import database
import uuid 

#TODO: SANITIZE ALL INPUT

mock_check = None
mock_id = None

def tux_check():
    if mock_check:
        return True 
    else:
        return True

def check_user():
    if mock_check:
        return True 
    else:
        return True

def check_admin():
    if mock_check:
        return True 
    else:
        return True

def get_admin():
    if mock_check:
        return True 
    else:
        return True

app = FastAPI()
db = database("utils/distros.json")
token = get_admin()

# View system gacha collection
@app.get("/user/gacha/all", status_code=200)
def user_gacha_all():
    if check_user():
        return db.get_all_gachas_user()
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View user personal gacha collection
mock_gacha_personal = None
@app.get("/user/gacha/collection", status_code=200)
def user_gacha_personal(id: str):
    if not check_user():
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
@app.get("/user/gacha/specific", status_code=200)
def user_gacha_specific(name : str):
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    gacha = db.get_specific_gacha(name,mock_id);
    if not gacha: 
        raise HTTPException(status_code=400, detail="Gacha not present")
    else:
        return gacha 

# Use In-Game Currency to Roll Gach
mock_gacha_roll = None
@app.get("/user/gacha/roll", status_code=200)
def user_gacha_roll(id: str):
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        if tux_check():
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
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_all_gachas_admin(mock_id)

# Admin View Specific Gacha
@app.get("/admin/gacha/specific", status_code=200)
def user_gacha_collection(name: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_specific_gacha(name,mock_id)

# Admin add Gacha
@app.get("/admin/gacha/add", status_code=200)
def user_gacha_modify(name: str, rarity: str, image: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_gacha(name,rarity,image,mock_id)
        if not res: 
            raise HTTPException(status_code=400, detail="Gacha already present")
        return res 

# Admin remove one Gacha 
@app.get("/admin/gacha/remove", status_code=200)
def user_gacha_modify(name: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_gacha(name)
        if not res: 
            raise HTTPException(status_code=400, detail="Invalid Name")
        return res 

# Admin Modify Specific Gacha by name 
@app.get("/admin/gacha/modify/specific", status_code=200)
def user_gacha(name: str,rarity: str, image: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.modify_gacha(name,rarity,image)
        if not res: 
            raise HTTPException(status_code=400, detail="Invalid Name")
        return res 

# Add user
@app.get("/admin/add/user", status_code=200)
def user_gacha(id: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user(id)
        if not res:
            raise HTTPException(status_code=400, detail="User already Present")
        else: 
            return res

# Delete user
@app.get("/admin/remove/user", status_code=200)
def user_gacha(id: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user(id)
        if not res:
            raise HTTPException(status_code=400, detail="User not Present")
        else: 
            return res

# get collection of a user
@app.get("/admin/get/user/collection", status_code=200)
def user_gacha(id: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        if mock_gacha_personal:
            res = db.get_user_gacha(1); 
        else: 
            res = db.get_user_gacha(id);
        if not res: 
            raise HTTPException(status_code=400, detail="User Not present")
        else: 
            return res

# add user gacha
@app.get("/admin/add/user/gacha", status_code=200)
def user_gacha(id: str, name: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user_gacha(id,name)
        if not res:
            raise HTTPException(status_code=400, detail="User not Present")
        elif res == 1: 
            raise HTTPException(status_code=400, detail="Gacha not Present")
        else: 
            return res

# delete user gacha
@app.get("/admin/remove/user/gacha", status_code=200)
def user_gacha(id: str, name: str):
    if not check_admin():
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