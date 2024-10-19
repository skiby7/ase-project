from fastapi import APIRouter, HTTPException, Body, Header

from libs.log import DEBUG, INFO, WARN, ERROR, log_level, log
import routers.registration.backend as rb

router = APIRouter()
