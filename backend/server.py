import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = os.getenv("MQTT_PORT", 1883)

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager
from time import time, sleep
import asyncio
import uvicorn
import logging
import argparse
import json

from services.log import logger
from routers import students, attendance, websocket
from database.db import DB

# =================================================================================================
# MQTT CLIENT =====================================================================================

async def run_activity(client, img_bytes):
    arduino_r4_payload = { "req": "ATTND" }
    frontend_payload = { "req": "ATTND" }

    try:
        result = await attendance.log_attendance_for_face_logic(img_bytes)
    except HTTPException as e:
        arduino_r4_payload["success"] = False
        frontend_payload["success"] = False

        if e.status_code == status.HTTP_400_BAD_REQUEST:
            arduino_r4_payload["msg"] = "No face found"
            frontend_payload["msg"] = "No face found in the given image"

        elif e.status_code == status.HTTP_404_NOT_FOUND:
            arduino_r4_payload["msg"] = "No match found"
            frontend_payload["msg"] = "Face does not match any student record"

        elif e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            arduino_r4_payload["msg"] = "Server error"
            frontend_payload["msg"] = "Server error. Please try again later!"

        elif e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            arduino_r4_payload["msg"] = "Server error"
            frontend_payload["msg"] = "Server error. Please try again later!"

    else:
        arduino_r4_payload["success"] = True
        arduino_r4_payload["msg"] = result["student"]["student_number"]

        frontend_payload["success"] = True
        frontend_payload["msg"] = f"Logged attendance for {result['student']['full_name']}"
        frontend_payload["student"] = result["student"]

    client.publish("arduino-r4/input", json.dumps(arduino_r4_payload))
    client.publish("frontend/attendance-log/response", json.dumps(frontend_payload))


def on_connect(client, flags, rc, properties):
    logger.info("Connected to MQTT")

def on_message(client, topic, payload, qos, properties):
    logger.info(f"Received on {topic}")

    if topic != "arduino-r4/output" and payload != "CLICK": return

    app = client._appdata.get("app")

    mode = app.state.mode
    img_bytes = app.state.img

    if mode != "ATTND" or img_bytes is None: return

    asyncio.create_task(run_activity(client, img_bytes))


def on_disconnect(client, packet, exc=None):
    logger.info("Disconnected from MQTT")
    if exc: logger.warning(f"Disconnect due to exception: {exc}")
    asyncio.create_task(reconnect(client))

async def reconnect(client):
    while True:
        try:
            logger.info("Attempting MQTT reconnect...")
            await client.connect(MQTT_BROKER, MQTT_PORT)
            logger.info("Reconnected to MQTT broker!")
            break
        except Exception as e:
            logger.warning(f"Reconnect failed: {e}")
            await asyncio.sleep(2)

# =================================================================================================
# APP CONTEXT =====================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mode = "ATTND"
    app.state.img = None

    client = MQTTClient("fastapi-backend")
    client._appdata = {"app": app}
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    for _ in range(10):
        try:
            await client.connect(MQTT_BROKER, MQTT_PORT)
        except ConnectionRefusedError:
            logger.info("MQTT broker unavailable, retrying in 2s...")
            await asyncio.sleep(2)
        else:
            await client.subscribe([("arduino-r4/output", 2)])
            app.state.mqtt_client = client
            break
    else:
        logger.error("Failed to connect to MQTT broker after 10 attempts")

    yield

    await client.disconnect()

app = FastAPI(lifespan=lifespan, root_path=CONTEXT_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: [{request.method}] {request.url.path}")

    start_time = time()
    response = await call_next(request)
    time_taken = time()-start_time

    logger.info(f"Response: [{response.status_code}][{time_taken:.2f} secs] {request.url.path}")
    return response

# =================================================================================================
# ROUTING ENDPOINTS ===============================================================================

app.include_router(students.router, prefix="/students")
app.include_router(attendance.router, prefix="/attendance")
app.include_router(websocket.router, prefix="/camera")

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)