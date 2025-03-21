from fastapi import WebSocket
from typing import Dict, List, Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.room_users: Dict[int, Set[int]] = {}  

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_users[room_id] = set()
        self.active_connections[room_id].append(websocket)
        self.room_users[room_id].add(user_id)

    def disconnect(self, websocket: WebSocket, room_id: int, user_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            self.room_users[room_id].discard(user_id)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                del self.room_users[room_id]

    async def broadcast(self, message: str, room_id: int):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

    def get_users_in_room(self, room_id: int) -> Set[int]:
        return self.room_users.get(room_id, set())

manager = ConnectionManager()