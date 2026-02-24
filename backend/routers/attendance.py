from fastapi import Request, APIRouter, status, HTTPException
from psycopg import OperationalError, InterfaceError, DatabaseError

from time import time

from database.db import DB
from services.log import logger
from services.image import Image, Face

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def get_attendance_logs():
    try:
        logs = DB.get_attendance_logs()
    except (OperationalError, InterfaceError):
        logger.exception("Get attendance logs [DATABASE CONNECTION ERROR]")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Please try again later."
        )
    except DatabaseError:
        logger.exception("Get attendance logs [DATABASE ERROR]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error"
        )

    if not logs:
        logger.info("Get all attendancec logs [NO LOGS FOUND]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attendance logs found")
    return logs

@router.post("/", status_code=status.HTTP_200_OK)
async def log_student_attendance(request: Request):
    img_bytes = await request.body()

    if not img_bytes:
        logger.info("Log student attendance [NO IMAGE DATA]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No image data")

    img = Image.get_decoded_img(img_bytes)

    now = time()
    is_valid_img = await Face.image_is_valid(img)
    logger.info(f"Image validation: {time()-now} secs")

    if not is_valid_img:
        logger.info("Log student attendance [IMAGE IS INVALID]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image"
        )
    
    now = time()
    embedding = await Image.get_embedding(img)
    logger.info(f"Image to embedding: {time()-now} secs")

    try:
        student_record = DB.log_attendance_for_face(embedding, 0.4)
    except (OperationalError, InterfaceError):
        logger.exception("Log student attendance [DATABASE CONNECTION ERROR]")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )
    except DatabaseError:
        logger.exception("Log student attendance [DATABASE ERROR]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

    if not student_record:
        logger.info("Log student attendance [NO STUDENT MATCHES THE IMAGE]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not a student"
        )

    return {
        "message": f"Logged for: {student_record['student_number']}",
        "student": student_record
    }