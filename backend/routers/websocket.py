from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("role") == "ARDUINO":
                manager.promote_to_arduino(websocket)
                continue

            await manager.broadcast_json(data, websocket)

            if manager.arduino_client and manager.arduino_client != websocket:
                await manager.send_to_arduino(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)