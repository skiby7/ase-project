from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from database.db import database
import uuid 

#TODO: SANITIZE ALL INPUT
 
def tux_check():
    return True 

def check_user():
    return True

def check_admin():
    return True

def get_admin():
    return True


# Inizializzazione DB
app = FastAPI()
db = database("utils/distros.json")
token = get_admin()

# View system gacha collection
@app.get("/user/gacha/all", status_code=201)
def user_gacha_all():
    if check_user():
        return db.get_all_gachas_user()
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View user personal gacha collection
@app.get("/user/gacha/personal", status_code=200)
def user_gacha_personal(id: str):
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        res = db.get_user_gacha(1); #TODO: uuid
        if not res: 
            raise HTTPException(status_code=400, detail="User Not present")
        else: 
            return res


# View Specific Gacha Info
@app.get("/user/gacha/specific", status_code=200)
def user_gacha_specific(name : str):
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    gacha = db.get_specific_gacha(name);
    if not gacha: 
        raise HTTPException(status_code=400, detail="Gacha not present")
    else:
        return gacha 

# Use In-Game Currency to Roll Gach
@app.get("/user/gacha/roll", status_code=200)
def user_gacha_roll():
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        if tux_check():
            return JSONResponse(content={"Name": db.get_roll_gacha()}) 
        else: 
            raise HTTPException(status_code=400, detail="ERROR")

# Admin View Gacha Collection
@app.get("/admin/gacha/collection", status_code=200)
def user_gacha_collection():
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        return db.get_all_gachas_admin()

# Admin add Gacha
@app.get("/admin/gacha/add", status_code=200)
def user_gacha_modify(name: str, rarity: str, image: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_gacha(name,rarity,image)
        if not res: 
            raise HTTPException(status_code=400, detail="Gacha already present")
        return res 

#  Admin remove one Gacha 
@app.get("/admin/gacha/remove", status_code=200)
def user_gacha_modify(name: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_gacha(name)
        if not res: 
            raise HTTPException(status_code=400, detail="Invalid Name")
        return res 

# TODO: Admin Modify Specific Gacha by name 
@app.get("/admin/gacha/modify/specific", status_code=200)
def user_gacha(name: str,rarity: str, image: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.modify_gacha(name,rarity,image)
        if not res: 
            raise HTTPException(status_code=400, detail="Invalid Name")
        return res 

# TODO: Add user
@app.get("admin/add/user", status_code=200)
def user_gacha(id: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user()
        if not res:
            raise HTTPException(status_code=400, detail="User already Present")
        else: 
            return res

# TODO: Delete user
@app.get("admin/remove/user", status_code=200)
def user_gacha(id: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user()
        if not res:
            raise HTTPException(status_code=400, detail="User not Present")
        else: 
            return res

# TODO: delete user gacha, from auction
@app.get("admin/add/user/gacha", status_code=200)
def user_gacha(id: str, name: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.add_user_gacha(id,name)
        if not res:
            raise HTTPException(status_code=400, detail="User or Gacha not Present")
        else: 
            return res

# TODO: add user gacha, from auction
@app.get("admin/remove/user/gacha", status_code=200)
def user_gacha(id: str, name: str):
    if not check_admin():
        raise HTTPException(status_code=400, detail="Invalid Admin")
    else: 
        res = db.remove_user_gacha(id,name)
        if not res:
            raise HTTPException(status_code=400, detail="User or Gacha not Present")
        else: 
            return res

