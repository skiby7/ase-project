import os
import json, yaml
import uvicorn
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers.buy import buy
from routers.transactions import transactions
from routers.admin import admin
from routers.payments import payments
from libs.db import create_tables


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
app.include_router(payments.router)
### Implementation ###

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
    create_tables()
    uvicorn.run("main:app", host="0.0.0.0", port=int(http_port), log_level=log_l)



if __name__ == "__main__":
    init()