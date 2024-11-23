from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from database.db import database
import uuid 

#TODO: non moccare db, moccare tux, doppio docker compose
#TODO: change path to /admin /user
#TODO: check user  
#TODO: jwt sub (uuid), role


# Inizializzazione DB
app = FastAPI()
db = database("utils/distros.json")

# View system gacha collection
@app.get("/user/gacha/all", status_code=200)
def user_gacha():
    return JSONResponse(content=db.get_all_distros_names())

# TODO: View user personal gacha collection
@app.get("/user/gacha/personal", status_code=200)
def user_gacha():
    return 

# TODO: View Specific Gacha Info
@app.get("/user/gacha/specific", status_code=200)
def user_gacha():
    return 

# TODO: Use In-Game Currency to Roll Gach
@app.get("/user/gacha/roll", status_code=200)
def user_gacha():
    return

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

# testing porpuses
@app.get("/add", status_code=200)
def add(a: int, b: int):
    if a is not int and b is not int:
        return {"s": a + b}
    else:
        raise HTTPException(status_code=400, detail="Invalid input")