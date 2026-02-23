from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []
        self.arduino_client: WebSocket = None

    def promote_to_arduino(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
        self.arduino_client = websocket

    def connect(self, websocket: WebSocket):
        if websocket not in self.connections:
            self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if self.arduino_client and websocket == self.arduino_client:
            self.arduino_client = None
        elif websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast_json(self, payload: dict, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            try:
                await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)

    async def broadcast_bytes(self, payload: bytes, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            try:
                await connection.send_bytes(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)
    
    async def send_to_arduino(self, payload: str):
        if self.arduino_client:
            await self.arduino_client.send_text(payload)


manager = ConnectionManager()