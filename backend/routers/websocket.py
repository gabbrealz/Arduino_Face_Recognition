from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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

            text = message.get("text")
            data = message.get("bytes")

            if text is not None:
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

                elif text == "CAPTURE":
                    print("Sent to arduino")
                    manager.send_to_arduino("CAPTURE")

            elif data is not None and receiving_image:
                image_chunks.append(data)

    finally:
        manager.disconnect(websocket)