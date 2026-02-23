import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")

from fastapi import FastAPI, Request
from asyncio_mqtt import Client
from contextlib import asynccontextmanager
from time import time
import asyncio
import uvicorn
import logging
import argparse

from services.log import logger
from routes import students, attendance
from database.db import DB

# =================================================================================================
# APP CONTEXT =====================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.state.mqtt_client = Client(MQTT_BROKER, MQTT_PORT)
    # await app.state.mqtt_client.connect()
    # asyncio.create_task(listen_to_topics())

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
# MQTT CLIENT =====================================================================================

# async def listen_to_topics():
#     async with app.state.mqtt_client.unfiltered_messages() as messages:
#         await app.state.mqtt_client.subscribe("camera/feed")

#         async for message in messages:
#             print(f"Received: {message.payload.decode()}")

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)