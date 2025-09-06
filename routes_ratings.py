
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from .db import get_db
from .models import Rating, Agent, Report, Task

router = APIRouter(prefix="/ratings", tags=["ratings"])

class RatingIn(BaseModel):
    agent_id: int
    dimension: str
    score: float

@router.post("")
def add_rating(payload: RatingIn, db: Session = Depends(get_db)):
    r = Rating(agent_id=payload.agent_id, dimension=payload.dimension, score=payload.score)
    db.add(r); db.flush()
    return {"id": r.id}

@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    rows = db.query(Rating.agent_id, Rating.dimension, func.avg(Rating.score).label("avg"))             .group_by(Rating.agent_id, Rating.dimension).all()
    out = {}
    for agent_id, dim, avg in rows:
        out.setdefault(agent_id, {})[dim] = float(avg)
    return out

@router.get("/flags/summary")
def flags_summary(db: Session = Depends(get_db)):
    # count reports per flag
    q = db.query(Report.flag, func.count(Report.id)).group_by(Report.flag).all()
    return {flag: count for flag, count in q}
