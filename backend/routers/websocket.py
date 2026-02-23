from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive()
            print(message)

            if message["type"] == "websocket.disconnect":
                break

            if "text" in message:
                text = message["text"]
                if text == "START":
                    receiving_image = True
                    image_chunks = []
                    continue
                elif text == "END":
                    receiving_image = False
                    full_image = b"".join(image_chunks)

                    await manager.broadcast_bytes(full_image, websocket)
                    continue
                elif text == "ARDUINO":
                    manager.promote_to_arduino(websocket)

            if "bytes" in message and receiving_image:
                image_chunks.append(message["bytes"])

    finally:
        manager.disconnect(websocket)