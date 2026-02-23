from fastapi import Request, APIRouter, status, HTTPException
from psycopg import OperationalError, InterfaceError, DatabaseError

from backend.database.db import DB
from backend.server import logger
from backend.services.image import Image, Face

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required")

    img = Image.get_decoded_img(img_bytes)
    is_valid_img = await Face.image_is_valid(img)

    if not is_valid_img:
        logger.info("Log student attendance [IMAGE IS INVALID]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is invalid. Please try again"
        )
    
    embedding = await Image.get_embedding(img)

    try:
        student_record = DB.log_attendance_for_face(embedding, 0.4)
    except (OperationalError, InterfaceError):
        logger.exception("Log student attendance [DATABASE CONNECTION ERROR]")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Please try again later."
        )
    except DatabaseError:
        logger.exception("Log student attendance [DATABASE ERROR]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error"
        )

    if not student_record:
        logger.info("Log student attendance [NO STUDENT MATCHES THE IMAGE]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The image does not match any registered student"
        )

    return {
        "message": f"Attendance logged successfully for {student_record['student_number']}",
        "student": student_record
    }