from fastapi import APIRouter, WebSocket
from services.connection_manager import manager

router = APIRouter()

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                print("Received disconnect message")
                break

            text = message.get("text")
            if text is not None:
                print("Received TEXT")
                await manager.broadcast(text)

            data = message.get("bytes")
            if data is not None:
                # print("Received BYTES")
                await manager.broadcast_bytes(data)

    finally:
        manager.disconnect(websocket)