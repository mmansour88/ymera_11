from typing import Dict, Set
from fastapi import WebSocket

class Hub:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def join(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    async def leave(self, room: str, ws: WebSocket):
        self.rooms.get(room, set()).discard(ws)

    async def broadcast(self, room: str, message: str):
        dead = []
        for ws in list(self.rooms.get(room, set())):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            await self.leave(room, d)

hub = Hub()
