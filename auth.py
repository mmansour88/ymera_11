
from fastapi import APIRouter
from pydantic import BaseModel
from ..auth.jwt_manager import create_token_pair
router = APIRouter()
class TokenIn(BaseModel):
    sub: str; org_id: int; team_ids: list[int]=[]; scopes: list[str]=[]
@router.post("/token")
def token(inp: TokenIn):
    return create_token_pair({"sub": inp.sub, "org_id": inp.org_id, "team_ids": inp.team_ids, "scopes": inp.scopes})
