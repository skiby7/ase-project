import os
from contextlib import asynccontextmanager
from logging import getLogger
from unittest.mock import patch

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .login import router as login_router
from .registration import router as registration_router
from .registration.services import initialize_admin
from .utils import logger
from .utils.app_config_utils import get_config_from_file, get_log_config
from .utils.mongo_connection import startup_db_client, delete_accounts_collection

logger = getLogger("uvicorn.error")

### Globals ###
script_path = os.path.dirname(os.path.abspath(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_db_client("db_authentication_test")
    delete_accounts_collection()
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

mocked_create_notify = patch("service.registration.services.notify_other_services_new_user",
                             return_value=None).start()

mocked_delete_notify = patch("service.registration.services.notify_other_services_delete_user",
                             return_value=None).start()

def init():
    http_port, log_l = get_config_from_file(script_path, logger)
    uvicorn.run("service.main_test:app", host="0.0.0.0", port=int(http_port), log_level=log_l,
                log_config=get_log_config(),
                ssl_keyfile="/run/secrets/ssl_private_key", ssl_certfile="/run/secrets/ssl_cert")


if __name__ == "__main__":
    init()
