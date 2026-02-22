import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

from fastapi import FastAPI, Request, Response, HTTPException, status
from contextlib import asynccontextmanager
from time import time
import asyncio
import uvicorn
import logging
import argparse

from psycopg.errors import UniqueViolation
from deepface import DeepFace
import cv2
import numpy as np

from database.db import DB
from models.request import CreateStudentRequestBody

# =================================================================================================
# HELPER FUNCTIONS ================================================================================

async def get_embedding(img_bytes):
    img_nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_nparr, cv2.IMREAD_COLOR)
    result = await asyncio.to_thread(DeepFace.represent, img, model_name="ArcFace")
    return result[0]["embedding"]

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
    logger.info(f"Incoming request: [{request.method}] {request.url.path}")

    start_time = time()
    response = await call_next(request)
    time_taken = time()-start_time

    logger.info(f"Response status: [{time_taken:.2f} secs] {response.status_code}")
    return response

# =================================================================================================
# API ENDPOINTS ===================================================================================

@app.get("/students", status_code=status.HTTP_200_OK)
async def get_students():
    students = DB.get_students()
    if not students:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students found")
    return students

@app.post("/students")
async def create_student(req_body: CreateStudentRequestBody):
    try:
        DB.insert_student(req_body.student_number, req_body.name, req_body.email)
    except UniqueViolation as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student number or email already exists")
    return {"message": "Student registered successfully"}

@app.post("/register-face/{student_number}", status_code=status.HTTP_201_CREATED)
async def register_face(student_number: str, request: Request):
    img_bytes = await request.body()

    if not img_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required")

    embedding = await get_embedding(img_bytes)
    face_registered = DB.register_face(student_number, embedding)

    if not face_registered:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return {"message": "Face registered successfully"}


@app.get("/attendance-logs", status_code=status.HTTP_200_OK)
async def get_attendance_logs():
    logs = DB.get_attendance_logs()
    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attendance logs found")
    return logs

@app.post("/attendance-logs", status_code=status.HTTP_200_OK)
async def log_student_attendance(request: Request):
    img_bytes = await request.body()
    
    if not img_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image data is required")

    embedding = await get_embedding(img_bytes)
    student_record = DB.log_attendance_for_face(embedding, 0.4)

    if not student_record:
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