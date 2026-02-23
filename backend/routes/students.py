from fastapi import APIRouter, status, HTTPException
from psycopg import OperationalError, InterfaceError, DatabaseError
from psycopg.errors import UniqueViolation

from backend.database.db import DB
from backend.server import logger
from backend.services.image import Image, Face
from backend.models.request import CreateStudentRequestBody

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def get_students():
    students = DB.get_students()
    if not students:
        logger.info("Get all students [NO STUDENTS FOUND]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students found")
    return students

@router.post("/")
async def create_student(req_body: CreateStudentRequestBody):
    try:
        DB.insert_student(req_body.student_number, req_body.name, req_body.email)
    except UniqueViolation as err:
        logger.info(f"Create student w/ email: {req_body.email} [UNIQUE CONSTRAINT VIOLATED]")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student number or email already exists")
    except DatabaseError as err:
        logger.exception(f"Create student w/ email: {req_body.email} [DATABASE ERROR]")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal database error")
    
    return {"message": "Student registered successfully"}

@router.post("/{student_number}/register-face", status_code=status.HTTP_201_CREATED)
async def register_face(student_number: str, request: Request):
    img_bytes = await request.body()

    if not img_bytes:
        logger.info(f"Register face for: {student_number} [NO IMAGE DATA]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required")

    img = Image.get_decoded_img(img_bytes)
    is_valid_img = await Face.image_is_valid(img)

    if not is_valid_img:
        logger.info("Log student attendance [NO IMAGE DATA]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is invalid. Please try again"
        )
    
    embedding = await Image.get_embedding(img)

    try:
        face_registered = DB.register_face(student_number, embedding)
    except (OperationalError, InterfaceError):
        logger.exception(f"Register face for: {student_number} [DATABASE CONNECTION ERROR]")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Please try again later."
        )
    except DatabaseError:
        logger.exception(f"Register face for: {student_number} [DATABASE ERROR]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database error"
        )

    if not face_registered:
        logger.info(f"Register face for: {student_number} [NO IMAGE DATA]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return {"message": "Face registered successfully"}