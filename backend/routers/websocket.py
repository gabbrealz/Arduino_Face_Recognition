from fastapi import APIRouter, WebSocket
from services.connection_manager import stream_manager, event_manager, microcontroller_manager

router = APIRouter()

@router.websocket("")
async def streaming_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive()

            data = message.get("bytes")
            if data is not None:
                print("Received BYTES")
                await stream_manager.broadcast_bytes(data, websocket)

    finally:
        stream_manager.disconnect(websocket)