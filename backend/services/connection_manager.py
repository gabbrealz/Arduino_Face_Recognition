from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    def connect(self, websocket: WebSocket):
        if websocket not in self.connections:
            self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: str, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            try:
                if connection != sender:
                    await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)

    async def broadcast_json(self, payload: dict, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            try:
                if connection != sender:
                    await connection.send_json(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)

    async def broadcast_bytes(self, payload: bytes, sender: WebSocket):
        dead_connections = []

        for connection in self.connections:
            try:
                if connection != sender:
                    await connection.send_bytes(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)
            

stream_manager = ConnectionManager()