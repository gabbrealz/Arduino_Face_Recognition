import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from gmqtt import Client as MQTTClient
from contextlib import asynccontextmanager
from time import time
import asyncio
import uvicorn
import logging
import argparse

from services.log import logger
from routers import students, attendance, websocket, modes
from database.db import DB

# =================================================================================================
# MQTT CLIENT =====================================================================================

def on_connect(client, flags, rc, properties):
    print("Connected to MQTT")
    client.subscribe("camera/feed")

def on_message(client, topic, payload, qos, properties):
    print(f"Received on {topic}")

def on_disconnect(client, packet, exc=None):
    logger.info("Disconnected from MQTT")

# =================================================================================================
# APP CONTEXT =====================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mode = "ATTENDANCE"

    try:
        client = MQTTClient("fastapi-client")
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        await client.connect(MQTT_BROKER, MQTT_PORT)
    except ConnectionRefusedError:
        pass
    else:
        app.state.mqtt_client = client

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
app.include_router(websocket.router, prefix="/ws")
app.include_router(modes.router, prefix="/modes")

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)