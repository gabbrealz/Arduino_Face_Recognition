from fastapi import Request, APIRouter, status, HTTPException
from psycopg import OperationalError, InterfaceError, DatabaseError

from time import time

from database.db import DB
from services.log import logger
from services.image import Image


router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
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
        logger.info("Get all attendance logs [LOGS IS EMPTY]")

    return logs


@router.delete("")
async def delete_attendance_log(id: int):
    try:
        DB.delete_attendance_log(id)
    except DatabaseError:
        logger.exception("Delete attendance log [DATABASE ERROR]")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal database error")
    
    return {"message": "Attendance log deleted successfully"}


async def log_attendance_for_face_logic(img):
    now = time()
    try:
        embedding = await Image.get_embedding(img)
    except ValueError:
        logger.info("Log student attendance [INVALID IMAGE]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is invalid")
    finally:
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