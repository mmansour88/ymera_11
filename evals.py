
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth.rbac import require_scope, TokenPayload

router = APIRouter()

class EvalRequest(BaseModel):
    suite: str = "quick"
    repeats: int = 1

@router.post("/run")
def run_eval(body: EvalRequest, auth: TokenPayload = Depends(require_scope("evals:run"))):
    # Minimal functional stub returning deterministic structure
    results = {"suite": body.suite, "scores": {"code": 0.72, "reasoning": 0.81, "support": 0.88}, "runs": body.repeats}
    return {"ok": True, "results": results}
