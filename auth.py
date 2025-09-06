import time, uuid, jwt
from fastapi import HTTPException, status
from passlib.hash import bcrypt
from ..config import settings
from ..models.tokens import RevokedToken
from sqlalchemy.orm import Session

def hash_password(p: str) -> str:
    return bcrypt.hash(p)

def verify_password(p: str, h: str) -> bool:
    return bcrypt.verify(p, h)

def _token(payload: dict, ttl: int) -> str:
    now = int(time.time())
    payload = {**payload, "iat": now, "exp": now + ttl, "jti": str(uuid.uuid4())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def create_pair(sub: str, roles=None, session_id:str="") -> dict:
    roles = roles or ["user"]
    base = {"sub": sub, "roles": roles, "sid": session_id}
    return {
        "access_token": _token({**base, "typ": "access"}, settings.ACCESS_TTL),
        "refresh_token": _token({**base, "typ": "refresh"}, settings.REFRESH_TTL),
    }

def verify_token(token: str, db: Session) -> dict:
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    jti = data.get("jti")
    if db.query(RevokedToken).filter_by(jti=jti).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    return data

def revoke_token(token: str, db: Session):
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG], options={"verify_exp": False})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token")
    jti = data.get("jti")
    if not jti:
        raise HTTPException(status_code=400, detail="No jti")
    db.add(RevokedToken(jti=jti))
    db.commit()
