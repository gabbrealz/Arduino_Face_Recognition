from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.connection_manager import stream_manager
from services.log import logger
from PIL import Image
import io

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
                
                img = Image.open(io.BytesIO(data))
                img = img.rotate(90, expand=True)

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG")
                rotated_bytes = buffer.getvalue()

                websocket.app.state.img = rotated_bytes
                await stream_manager.broadcast_bytes(rotated_bytes, websocket)

    except (WebSocketDisconnect, RuntimeError):
        logger.info("A websocket connection disconnected")

    finally:
        stream_manager.disconnect(websocket)