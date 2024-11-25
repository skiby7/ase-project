import os
import json, yaml
import uvicorn
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid 

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

### DB init ###
db = database("utils/distros.json")

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
            config = yaml.load(f.read(), Loader=yaml.Loader)
        http_port = config.get("http_port", 9090)
        log_l = config.get("log_level", "info")

        logger.debug(f"Configuration: {json.dumps(config, indent=4)}")
    else:
        logger.warning("Configuration file not found!")
        log_l = "debug"
    logger.info("Starting v1.0.0")

    uvicorn.run("main:app", host="0.0.0.0", port=int(http_port), log_level=log_l)


#DB NOTES
#bidded auction and owned auctions separated


#[PLAYER]
##API
# create auction
@app.post("/create")
def create():
    #ask collection for list of owned gachas
    #let the player choose between them
    #ask collection to lock the gacha
    #let the player decide a price
    #let the player decide a time of start and stop
    #NB may have to decide constraints on time
    #add to currently ongoing auctions of the player
    pass
# place bid on auction
@app.post("/bid")
def bid(price): #as an argument the bid
    #take for assumption client makes only higher bids?
    #freeze the amount via tux service
    #add to bidded auctions
    pass
# enable view of auction history
@app.post("/auctionHistory")
def auctionHistory(): 
    pass






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
def marketActivity():
    pass
# Enable view details of auction
@app.get("/auctionInfo")
def auctionInfo():
    pass
# Enable manipulation of auction
@app.post("/auctionModify")
def auctionModify():
    pass
# Enable to see all time history
@app.post("/history")
def history():
    pass

#[SECURITY]
##LOGIC
# Security - no auction listing manipulations

if __name__ == "__main__":
    init()
