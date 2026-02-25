from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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
            message = await websocket.receive()

            data = message.get("bytes")
            if data is not None:
                # print("Received BYTES")
                websocket.app.state.img = data
                await stream_manager.broadcast_bytes(data, websocket)

    except (WebSocketDisconnect, RuntimeError):
        logger.info("A websocket connection disconnected")

    finally:
        stream_manager.disconnect(websocket)