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

# Inizializzazione DB
app = FastAPI()
db = database("utils/distros.json")

# View system gacha collection
@app.get("/user/gacha/all", status_code=201)
def user_gacha_all():
    if check_user():
        return db.get_all_gachas_user()
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View user personal gacha collection
@app.get("/user/gacha/personal", status_code=200)
def user_gacha_personal():
    if check_user():
        return db.get_user_gacha(1); #TODO: uuid
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

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
@app.get("user/add", status_code=200)
def user_gacha():
    return

# TODO: Delete user
@app.get("user/remove", status_code=200)
def user_gacha():
    return