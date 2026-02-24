from fastapi import APIRouter, WebSocket
from services.connection_manager import stream_manager, event_manager

router = APIRouter()

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                print("Received disconnect message")
                break

            text = message.get("text")
            if text is not None:
                print("Received TEXT")
                await stream_manager.broadcast(text, websocket)

            data = message.get("bytes")
            if data is not None:
                # print("Received BYTES")
                await stream_manager.broadcast_bytes(data, websocket)

    finally:
        stream_manager.disconnect(websocket)


@router.websocket("/event")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    event_manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                print("Received disconnect message")
                break

            text = message.get("text")
            if text is not None:
                print("Received TEXT")
                await event_manager.broadcast(text, websocket)

    finally:
        event_manager.disconnect(websocket)