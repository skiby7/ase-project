from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from database.db import database
import uuid 

#TODO: non moccare db, moccare tux, doppio docker compose
#TODO: change path to /admin /user
#TODO: check user  
#TODO: jwt sub (uuid), role

def check_user():
    return True

# Inizializzazione DB
app = FastAPI()
db = database("utils/distros.json")

# View system gacha collection
@app.get("/user/gacha/all", status_code=200)
def user_gacha():
    if check_user():
        return db.get_all_gachas_name()
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View user personal gacha collection
@app.get("/user/gacha/personal", status_code=200)
def user_gacha():
    if check_user():
        return db.get_user_gacha(1);
    else: 
        raise HTTPException(status_code=400, detail="Invalid User")

# View Specific Gacha Info
@app.get("/user/gacha/specific", status_code=200)
def user_gacha(name : str):
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    gacha = db.get_specific_gacha(name);
    if not gacha: 
        raise HTTPException(status_code=400, detail="Gacha not present")
    else:
        return gacha 

# TODO: Use In-Game Currency to Roll Gach, TODO: userid, with tux
@app.get("/user/gacha/roll", status_code=200)
def user_gacha():
    if not check_user():
        raise HTTPException(status_code=400, detail="Invalid User")
    else: 
        return JSONResponse(content={"name": db.get_random_gacha()})

# TODO: Admin View Gacha Collection
@app.get("/admin/gacha/collection", status_code=200)
def user_gacha():
    return

# TODO: Admin Modify Gacha Collection, insert or delete new gacha
@app.get("/admin/gacha/modify", status_code=200)
def user_gacha():
    return

# TODO: Admin Modify Specific Gacha
@app.get("/admin/gacha/modify/specific", status_code=200)
def user_gacha():
    return

# TODO: Add user
@app.get("user/notify/add", status_code=200)
def user_gacha():
    return

# TODO: Delete user
@app.get("user/notify/add", status_code=200)
def user_gacha():
    return

# testing porpuses
@app.get("/add", status_code=200)
def add(a: int, b: int):
    if a is not int and b is not int:
        return {"s": a + b}
    else:
        raise HTTPException(status_code=400, detail="Invalid input")