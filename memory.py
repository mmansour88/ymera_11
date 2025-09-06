
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth.rbac import require_scope, TokenPayload
from ..db import get_db
from ..services.memory import upsert_memory, embed_text, search_memory

router = APIRouter()

class UpsertBody(BaseModel):
    namespace: str
    key: str
    text: str

@router.post("/upsert")
async def upsert(body: UpsertBody, auth: TokenPayload = Depends(require_scope("memory:write")), db: Session = Depends(get_db)):
    return await upsert_memory(db, auth.org_id, body.namespace, body.key, body.text)

class SearchBody(BaseModel):
    namespace: str
    query: str
    top_k: int = 5

@router.post("/search")
async def search(body: SearchBody, auth: TokenPayload = Depends(require_scope("memory:read")), db: Session = Depends(get_db)):
    vec = await embed_text(body.query)
    return search_memory(db, auth.org_id, body.namespace, vec, body.top_k)
