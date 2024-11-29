import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .login import router as login_router
from .registration import router as registration_router
from .registration.services import initialize_admin
from .utils.logger import logger
from .utils.app_config_utils import get_config_from_file, get_log_config
from .utils.mongo_connection import startup_db_client

### Globals ###
script_path = os.path.dirname(os.path.abspath(__file__))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    startup_db_client()
    initialize_admin()
    yield

### App init ###
app = FastAPI(lifespan=lifespan)
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


def init():
    http_port, log_l = get_config_from_file(script_path, logger)
    uvicorn.run("service.main:app", host="0.0.0.0", port=int(http_port), log_level=log_l,
                log_config=get_log_config(),
                ssl_keyfile="/run/secrets/ssl_private_key", ssl_certfile="/run/secrets/ssl_cert")

if __name__ == "__main__":
    init()
