
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth.rbac import require_scope, TokenPayload
from ..db import get_db
from ..services.skills import record_score, top_teachers
from ..services.rewards import reward_teacher

router = APIRouter()

class ScoreIn(BaseModel):
    agent_id: str
    skill: str
    score: float

@router.post("/score")
def score(body: ScoreIn, _: TokenPayload = Depends(require_scope("agents:score")), db: Session = Depends(get_db)):
    record_score(db, body.agent_id, body.skill, body.score)
    return {"ok": True}

class DistillIn(BaseModel):
    teacher_id: str
    learner_id: str
    skill: str

@router.post("/distill")
def distill(body: DistillIn, __: TokenPayload = Depends(require_scope("agents:teach")), db: Session = Depends(get_db)):
    # Simplified: award teacher immediately; in production this would launch a job
    reward_teacher(db, body.teacher_id, 10, f"Distilled {body.skill} to {body.learner_id}")
    return {"ok": True, "awarded": 10}

@router.get("/top")
def top(skill: str, k: int = 3, _: TokenPayload = Depends(require_scope("agents:score")), db: Session = Depends(get_db)):
    rows = top_teachers(db, skill, k)
    return [{"agent_id": r[0], "avg": float(r[1])} for r in rows]
