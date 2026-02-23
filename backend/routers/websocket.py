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
            print(message)

            if message["type"] == "websocket.disconnect":
                break

            data = message.get("bytes")
            if data is not None:
                await manager.broadcast_bytes(data, websocket)

    finally:
        manager.disconnect(websocket)