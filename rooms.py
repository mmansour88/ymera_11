
import os, json, time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import redis
from ..auth.rbac import require_scope, TokenPayload

router = APIRouter()
r = redis.Redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"), decode_responses=True)

class CreateRoom(BaseModel):
    room_id: str
    meta: dict | None = None

@router.post("/create")
def create_room(body: CreateRoom, auth: TokenPayload = Depends(require_scope("rooms:manage"))):
    key = f"room:{body.room_id}"
    if r.exists(key):
        raise HTTPException(409, "room_exists")
    r.hset(key, mapping={"created_at": str(int(time.time())), "meta": json.dumps(body.meta or {})})
    r.expire(key, 60*60*12)
    return {"ok": True}

class JoinRoom(BaseModel):
    room_id: str
    peer_id: str
    sdp: str

@router.post("/join")
def join_room(body: JoinRoom, auth: TokenPayload = Depends(require_scope("rooms:join"))):
    key = f"room:{body.room_id}:peers"
    r.hset(key, body.peer_id, body.sdp)
    r.expire(key, 60*60*4)
    return {"ok": True}

@router.get("/peers")
def peers(room_id: str, auth: TokenPayload = Depends(require_scope("rooms:join"))):
    key = f"room:{room_id}:peers"
    return r.hgetall(key)
