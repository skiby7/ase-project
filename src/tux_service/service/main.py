import os
import json, yaml
import uvicorn
from logging import getLogger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.buy import buy
from routers.transactions import transactions
from routers.admin import admin
from routers.roll import roll
from routers.balances import balances
from libs.db.db import create_tables


### Globals ###
script_path = os.path.dirname(os.path.abspath(__file__))
logger = getLogger("uvicorn.error")

### App init ###
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[]
)
app.include_router(buy.router)
app.include_router(transactions.router)
app.include_router(admin.router)
app.include_router(roll.router)
app.include_router(balances.router)

### Implementation ###

def init():
    global log_level
    config_path = os.path.join(script_path, "config.yml")
    http_port = 9090
    cert_file = None
    key_file = None
    if os.path.isfile(config_path):

        with open(config_path, "r") as f:
            config = yaml.safe_load(f.read())

        http_port = config.get("http_port", 9090)
        log_l = config.get("log_level", "info")
        cert_file = config.get("cert_file")
        key_file = config.get("key_file")
        logger.debug(f"Configuration: {json.dumps(config, indent=4)}")
    else:
        logger.warning("Configuration file not found!")
        log_l = "debug"
    logger.info("Starting v1.0.0")
    create_tables()
    uvicorn.run("main:app",
        host="0.0.0.0",
        port=int(http_port),
        log_level=log_l,
        ssl_keyfile=key_file,
        ssl_certfile=cert_file
    )



if __name__ == "__main__":
    init()
