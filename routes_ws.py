from fastapi import APIRouter, WebSocket, WebSocketDisconnect
router = APIRouter(prefix="/ws", tags=["ws"])

clients = set()

@router.websocket("/live")
async def live(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            for c in list(clients):
                try:
                    await c.send_text(data)
                except:
                    pass
    except WebSocketDisconnect:
        clients.discard(ws)
