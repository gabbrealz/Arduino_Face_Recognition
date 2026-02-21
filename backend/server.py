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
    logger.info(f"Incoming request: [{request.method}] {request.url.path}")
    start_time = time()
    response = await call_next(request)
    logger.info(f"Response status: [{time()-start_time:.2f} secs] {response.status_code}")
    return response

# =================================================================================================
# API ENDPOINTS ===================================================================================

@app.post("/students")
async def create_student(data: CreateStudentRequestBody):
    pass

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)