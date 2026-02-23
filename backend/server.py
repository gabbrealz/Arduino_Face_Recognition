import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")

from fastapi import FastAPI, Request, Response, HTTPException, status
from asyncio_mqtt import Client
from contextlib import asynccontextmanager
from time import time
import asyncio
import uvicorn
import logging
import argparse

from psycopg import OperationalError, InterfaceError, DatabaseError
from psycopg.errors import UniqueViolation
from deepface import DeepFace
import cv2
import numpy as np

from database.db import DB
from models.request import CreateStudentRequestBody

# =================================================================================================
# APP CONTEXT =====================================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan, root_path=CONTEXT_PATH)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: [{request.method}] {request.url.path}")

    start_time = time()
    response = await call_next(request)
    time_taken = time()-start_time

    logger.info(f"Response: [{response.status_code}][{time_taken:.2f} secs] {request.url.path}s")
    return response

# =================================================================================================
# HELPER FUNCTIONS ================================================================================

def get_decoded_img(img_bytes):
    img_nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(img_nparr, cv2.IMREAD_COLOR)

async def image_is_valid(img):
    faces = await asyncio.to_thread(
        DeepFace.extract_faces,
        img_path=img,
        detector_backend="retinaface",
        enforce_detection=False,
        anti_spoofing=True)

    if len(faces) > 0: return True
    return False

async def get_embedding(img):
    result = await asyncio.to_thread(DeepFace.represent, img, model_name="ArcFace")
    return result[0]["embedding"]

# =================================================================================================
# API ENDPOINTS ===================================================================================

@app.get("/students", status_code=status.HTTP_200_OK)
async def get_students():
    students = DB.get_students()
    if not students:
        logger.info("Get all students [NO STUDENTS FOUND]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students found")
    return students

@app.post("/students")
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

@app.post("/students/{student_number}/register-face", status_code=status.HTTP_201_CREATED)
async def register_face(student_number: str, request: Request):
    img_bytes = await request.body()

    if not img_bytes:
        logger.info(f"Register face for: {student_number} [NO IMAGE DATA]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required")

    img = get_decoded_img(img_bytes)
    is_valid_img = await image_is_valid(img)

    if not is_valid_img:
        logger.info("Log student attendance [NO IMAGE DATA]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is invalid. Please try again"
        )
    
    embedding = await get_embedding(img)

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


@app.get("/students/attendance", status_code=status.HTTP_200_OK)
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

@app.post("/students/attendance", status_code=status.HTTP_200_OK)
async def log_student_attendance(request: Request):
    img_bytes = await request.body()

    if not img_bytes:
        logger.info("Log student attendance [NO IMAGE DATA]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required")

    img = get_decoded_img(img_bytes)
    is_valid_img = await image_is_valid(img)

    if not is_valid_img:
        logger.info("Log student attendance [IMAGE IS INVALID]")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is invalid. Please try again"
        )
    
    embedding = await get_embedding(img)

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

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)