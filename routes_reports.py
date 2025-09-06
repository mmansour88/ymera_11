from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from .db import get_db
from .models import Report
router = APIRouter(prefix="/reports", tags=["reports"])
class ReportIn(BaseModel):
    task_id:int; summary:str; flag:str="green"
@router.post("")
def create_report(payload: ReportIn, db: Session = Depends(get_db)):
    r=Report(task_id=payload.task_id, summary=payload.summary, flag=payload.flag, created_at=datetime.utcnow())
    db.add(r); db.flush()
    return {"id":r.id}
@router.get("")
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.id.desc()).all()
