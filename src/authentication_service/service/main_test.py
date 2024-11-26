import json
import os
import yaml
from logging import getLogger

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .login import router as login_router
from .registration import router as registration_router
from .registration.services import initialize_admin
from .utils.mongo_connection import startup_db_client, delete_accounts_collection

logger = getLogger("uvicorn.error")

### Globals ###
script_path = os.path.dirname(os.path.abspath(__file__))

### App init ###
app = FastAPI()
app.include_router(login_router.router)
app.include_router(login_router.admin_router)
app.include_router(registration_router.router)
app.include_router(registration_router.admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[]
)

@app.on_event("startup")
def startup_event():
    startup_db_client("db_authentication_test")
    delete_accounts_collection()
    initialize_admin()

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

if __name__ == "__main__":
    init()
