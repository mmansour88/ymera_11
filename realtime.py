from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

router = APIRouter()

class SignalingHub:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def join(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    async def leave(self, room: str, ws: WebSocket):
        self.rooms.get(room, set()).discard(ws)

    async def relay(self, room: str, payload: str, sender: WebSocket):
        dead = []
        for peer in list(self.rooms.get(room, set())):
            if peer is sender: continue
            try:
                await peer.send_text(payload)
            except Exception:
                dead.append(peer)
        for d in dead:
            await self.leave(room, d)

hub = SignalingHub()

@router.websocket("/signal/{room}")
async def signal(ws: WebSocket, room: str):
    await hub.join(room, ws)
    try:
        while True:
            msg = await ws.receive_text()
            await hub.relay(room, msg, ws)
    except WebSocketDisconnect:
        await hub.leave(room, ws)
