from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []
        self.arduino_client: WebSocket = None

    def promote_to_arduino(self, websocket: WebSocket):
        self.connections.remove(websocket)
        self.arduino_client = websocket

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if self.arduino_client and websocket == self.arduino_client:
            self.arduino_client = None
        elif websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast_json(self, payload: dict, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            if connection == sender: continue
            try:
                await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)

    async def broadcast_bytes(self, payload: bytes, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            if connection == sender: continue
            try:
                await connection.send_bytes(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)
    
    async def send_to_arduino(self, payload: dict):
        if self.arduino_client != None:
            await self.arduino_client.send_json(payload)