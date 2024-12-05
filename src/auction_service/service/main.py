import os
import json, yaml
import uvicorn
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

### Globals ###
script_path = os.path.dirname(os.path.abspath(__file__))
logger  = getLogger('uvicorn.error')


### App init ###
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[]
)

### Implementation ###
@app.get("/")
def home():
    return { "status": "ok" }

def init():
    global log_level
    config_path = os.path.join(script_path, "config.yml")
    http_port = 9090
    if os.path.isfile(config_path):

        with open(config_path, "r") as f:
            config = yaml.safe_load(f.read())
        http_port = config.get("http_port", 9090)
        log_l = config.get("log_level", "info")

        logger.debug(f"Configuration: {json.dumps(config, indent=4)}")
    else:
        logger.warning("Configuration file not found!")
        log_l = "debug"
    logger.info("Starting v1.0.0")

    uvicorn.run("main:app", host="0.0.0.0", port=int(http_port), log_level=log_l)

#[PLAYER]
##API
# create auction
@app.post("/create")
def create():
    pass
# place bid on auction
@app.post("/bid")
def bid(): #as an argument the bid
    pass
# [ON HOLD] enable view of transaction history
##LOGIC
# Deliver won gacha after auction
# Deliver tux to auction creator after end
# Give back tux if lost auction
#---> service should always watch over currently on going auctions
#---> if time elapsed behave as needed

#[ADMIN]
##API
# Enable seeing market history of a player
@app.get("/auctionHistoryPlayer")
def auctionHistoryPlayer():
    pass
# Enable to see market auction activity
@app.get("/marketActivity")
def auctionHistoryPlayer():
    pass
# Enable view details of auction
@app.get("/auctionInfo")
def auctionHistoryPlayer():
    pass
# Enable manipulation of auction
@app.post("/auctionModify")
def auctionHistoryPlayer():
    pass
# Enable to see all time history
@app.post("/history")
def auctionHistoryPlayer():
    pass

#[SECURITY]
##LOGIC
# Security - no auction listing manipulations

if __name__ == "__main__":
    init()
