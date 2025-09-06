
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth.rbac import require_scope, TokenPayload
from ..db import get_db
from ..services.governance import EscalationPolicy, grade_flag, DEFAULT, suspend_team, resume_team, is_team_suspended

router = APIRouter()
_policy = DEFAULT

class PolicyIn(BaseModel):
    orange_threshold: float = 0.4
    red_threshold: float = 0.7
    auto_shutdown_on_red: bool = True

@router.get("/policy")
def get_policy(_: TokenPayload = Depends(require_scope("admin:read"))):
    return _policy.__dict__

@router.post("/policy")
def set_policy(body: PolicyIn, __: TokenPayload = Depends(require_scope("admin:write"))):
    global _policy
    _policy = EscalationPolicy(**body.model_dump())
    return {"ok": True, "policy": _policy.__dict__}

class EvaluateIn(BaseModel):
    risk_score: float
    team_id: int | None = None

@router.post("/evaluate")
def evaluate(body: EvaluateIn, _: TokenPayload = Depends(require_scope("admin:read"))):
    flag = grade_flag(body.risk_score, _policy)
    out = {"flag": flag}
    if body.team_id is not None and flag == "red" and _policy.auto_shutdown_on_red:
        out["action"] = suspend_team(body.team_id)
    return out

@router.post("/teams/suspend")
def suspend(team_id: int, __: TokenPayload = Depends(require_scope("admin:write"))):
    return suspend_team(team_id)

@router.post("/teams/resume")
def resume(team_id: int, __: TokenPayload = Depends(require_scope("admin:write"))):
    return resume_team(team_id)

@router.get("/teams/status")
def status(team_id: int, ___: TokenPayload = Depends(require_scope("admin:read"))):
    return {"team_id": team_id, "suspended": is_team_suspended(team_id)}

