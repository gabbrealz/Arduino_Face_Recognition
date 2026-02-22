import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

from fastapi import FastAPI, Request, Response, status
from contextlib import asynccontextmanager
from time import time
import asyncio
import uvicorn
import logging
import argparse

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

@app.get("/students")
async def get_students():
    return DB.get_students()

@app.post("/students")
async def create_student(data: CreateStudentRequestBody):
    DB.insert_student(data.student_number, data.name, data.email)


@app.get("/attendance-logs")
async def get_attendance_logs():
    return DB.get_attendance_logs()

@app.post("/attendance-logs")
async def log_student_attendance(request: Request):
    img_bytes = await request.body()
    embedding = await get_embedding(img_bytes)
    student_record = DB.log_attendance_for_face(embedding, 0.4)

    if student_record is None:
        return {
            "success": False,
            "message": "The image does not match any registered student"
        }
    
    return {
        "success": True,
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