
import os, uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth.rbac import require_scope, TokenPayload
from ..services.storage_s3 import sign_post_policy, sign_put_url

router = APIRouter()

class SignUploadRequest(BaseModel):
    key_prefix: str = "uploads/"
    content_type: str = "application/octet-stream"
    max_size_mb: int = 25
    method: str = "post"

@router.post("/sign-upload")
def sign_upload(req: SignUploadRequest, auth: TokenPayload = Depends(require_scope("files:write"))):
    bucket = os.getenv("S3_BUCKET","ymera-dev")
    if req.method == "post":
        return sign_post_policy(bucket=bucket, key_prefix=f"{auth.org_id}/{req.key_prefix}", content_type=req.content_type, max_mb=req.max_size_mb)
    elif req.method == "put":
        return {"url": sign_put_url(bucket=bucket, key=f"{auth.org_id}/{req.key_prefix}{uuid.uuid4()}")}
    else:
        raise HTTPException(400, "invalid_method")
