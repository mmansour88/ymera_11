
import os, time, jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List

auth_router = APIRouter()
bearer = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET","dev-secret-change")
JWT_ISS = os.getenv("JWT_ISS","ymera")
JWT_AUD = os.getenv("JWT_AUD","ymera-clients")
JWT_EXP = int(os.getenv("JWT_EXP_SECONDS","3600"))

class TokenPayload(BaseModel):
    sub: str
    org_id: int
    team_ids: List[int] = []
    scopes: List[str] = []

def create_token(payload: TokenPayload) -> str:
    data = payload.dict()
    now = int(time.time())
    claims = {"iss": JWT_ISS, "aud": JWT_AUD, "iat": now, "exp": now + JWT_EXP, **data}
    return jwt.encode(claims, JWT_SECRET, algorithm="HS256")

def require_auth(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> TokenPayload:
    token = creds.credentials
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience=JWT_AUD, issuer=JWT_ISS)
        return TokenPayload(**{k: data[k] for k in ["sub","org_id","team_ids","scopes"]})
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")

def require_scope(scope: str):
    def dep(payload: TokenPayload = Depends(require_auth)):
        if scope not in payload.scopes and "admin:*" not in payload.scopes:
            raise HTTPException(status_code=403, detail="insufficient_scope")
        return payload
    return dep

class TokenRequest(BaseModel):
    sub: str
    org_id: int
    team_ids: List[int] = []
    scopes: List[str] = []

@auth_router.post("/token")
def issue_token(req: TokenRequest):
    return {"access_token": create_token(TokenPayload(**req.dict()))}
