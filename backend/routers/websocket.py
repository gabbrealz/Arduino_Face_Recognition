import numpy as np
import cv2
from deepface import DeepFace
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from services.image import Image
from services.connection_manager import stream_manager
from services.log import logger

router = APIRouter()

@router.websocket("")
async def streaming_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_manager.connect(websocket)
    logger.info("New websocket connection!")

    try:
        while True:
            data = await websocket.receive_bytes()

            # print("Received BYTES")
            
            img = Image.get_decoded_img(data, rotate=True)
            websocket.app.state.img = img

            if not websocket.app.state.face_detection_running:
                websocket.app.state.face_detection_running = True
                asyncio.create_task(alert_if_face_found(websocket.app, img))

            _, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            await stream_manager.broadcast_bytes(buffer.tobytes(), websocket)

    except (WebSocketDisconnect, RuntimeError):
        logger.info("A websocket connection disconnected")

    finally:
        stream_manager.disconnect(websocket)


async def alert_if_face_found(app, img):
    try:
        faces = await asyncio.to_thread(DeepFace.extract_faces, img, enforce_detection=False, anti_spoofing=True)
        face_found = any(face["is_real"] for face in faces)
        app.state.mqtt_client.publish("fastapi/capture/face-found", "T" if face_found else "F", qos=0)
    finally:
        app.state.face_detection_running = False