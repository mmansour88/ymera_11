from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
import os
router = APIRouter(prefix="/auth", tags=["auth"])
JWT_SECRET=os.getenv("JWT_SECRET","dev-secret")
JWT_ALG=os.getenv("JWT_ALG","HS256")
class Login(BaseModel):
    email:str; password:str
@router.post("/login")
def login(payload: Login):
    if payload.email!="admin@example.com" or payload.password!="admin":
        raise HTTPException(401, "invalid credentials")
    now=datetime.utcnow()
    claims={"sub":payload.email,"role":"admin","iat":int(now.timestamp()),"exp":int((now+timedelta(hours=8)).timestamp())}
    token=jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token":token,"token_type":"bearer"}
