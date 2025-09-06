
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json, asyncio
from .redis_conn import get_redis

router = APIRouter(prefix="/ws", tags=["webrtc"])

# Simple room signaling broker over Redis pubsub
@router.websocket("/rooms/{room_id}")
async def room_socket(ws: WebSocket, room_id: str):
    await ws.accept()
    r = await get_redis()
    channel = f"ymera:room:{room_id}"
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    try:
        async def forward_pub():
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    await ws.send_text(msg["data"].decode())

        forward_task = asyncio.create_task(forward_pub())
        while True:
            raw = await ws.receive_text()
            # Re-broadcast to room
            await r.publish(channel, raw)
    except WebSocketDisconnect:
        pass
    finally:
        forward_task.cancel()
        await pubsub.unsubscribe(channel)
