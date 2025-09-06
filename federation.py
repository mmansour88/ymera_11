from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.metrics import AgentScore

router = APIRouter()

@router.post("/federation/ingest")
def ingest(agent_id: int, task_type: str, success: float, samples: int = 1, db: Session = Depends(get_db)):
    row = AgentScore(agent_id=agent_id, task_type=task_type, success_rate=success, samples=samples)
    db.add(row); db.commit()
    return {"ok": True}

@router.get("/federation/routing")
def routing(task_type: str, db: Session = Depends(get_db)):
    rows = db.query(AgentScore).filter_by(task_type=task_type).all()
    total = sum(r.success_rate for r in rows) or 1.0
    return [{"agent_id": r.agent_id, "weight": r.success_rate/total} for r in rows]
