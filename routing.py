
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth.rbac import require_scope, TokenPayload

router = APIRouter()

class RouteRequest(BaseModel):
    task_type: str = "general"
    desired_quality: str = "balanced"

@router.post("")
def choose_model(body: RouteRequest, auth: TokenPayload = Depends(require_scope("routing:read"))):
    # Simple policy
    policy = {
        ("general","balanced"): "groq-llama-3.3-70b",
        ("code","high"): "anthropic-claude-3.7-sonnet",
        ("vision","balanced"): "openai-gpt-4o-mini",
        ("general","cheap"): "deepseek-r1-lite"
    }
    model = policy.get((body.task_type, body.desired_quality), "groq-llama-3.3-70b")
    return {"model": model}
