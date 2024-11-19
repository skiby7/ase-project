from fastapi import APIRouter, HTTPException, Body, Header

import authentication_service.service.routers.registration.services as rb

router = APIRouter()
