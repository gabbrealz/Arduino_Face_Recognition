from fastapi import Request, APIRouter, status, HTTPException
from psycopg import OperationalError, InterfaceError, DatabaseError
from psycopg.errors import UniqueViolation

from time import time

from database.db import DB
from services.log import logger
from services.image import Image, Face
from models.request import CreateStudentRequestBody

router = APIRouter()

@router.get("/image-endpoint")
async def get_image_endpoint(request: Request):
    mode = request.app.state.mode

    if mode == "ATTENDANCE":
        return {"endpoint": "/attendance/"}
    elif mode == "REGISTER":
        return {"endpoint": "/students/"}

@router.post("/image-endpoint")
async def get_image_endpoint(request: Request, mode: str):
    request.app.state.mode = mode