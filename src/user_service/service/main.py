import os
import json, yaml
import uvicorn
from logging import getLogger
from pydantic import BaseModel
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from user_service.service.routers import user


logger = getLogger("uvicorn.error")

### Globals ###
script_path = os.path.dirname(os.path.abspath(__file__))

### App init ###
app = FastAPI()
app.include_router(user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[]
)

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
