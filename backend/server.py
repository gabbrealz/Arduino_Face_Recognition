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

from routes import students, attendance
from database.db import DB

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
# ROUTING ENDPOINTS ===============================================================================

app.include_router(students.router, prefix="/students")
app.include_router(attendance.router, prefix="/attendance")

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)