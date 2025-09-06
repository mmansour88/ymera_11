from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.collab import Report
from ..services.rules import auto_flag
from ..services.events_persistent import enqueue

router = APIRouter()

@router.post("/reports/auto")
def reports_auto(project_id: int, metrics: dict = Body(...), db: Session = Depends(get_db)):
    level = auto_flag(metrics)
    rep = Report(project_id=project_id, level=level, details=str(metrics))
    db.add(rep); db.commit()
    enqueue("reports", {"project_id": project_id, "level": level, "metrics": metrics})
    return {"id": rep.id, "level": level}
