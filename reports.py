
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth.rbac import require_scope, TokenPayload
from ..db import get_db
from ..models import Report

router = APIRouter()

class ReportCreate(BaseModel):
    team_id: int | None = None
    task_id: str | None = None
    level: str = "green"
    summary: str | None = None
    details: dict | None = None

@router.post("")
def create_report(body: ReportCreate, auth: TokenPayload = Depends(require_scope("reports:write")), db: Session = Depends(get_db)):
    report = Report(org_id=auth.org_id, **body.dict())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("")
def list_reports(auth: TokenPayload = Depends(require_scope("reports:read")), db: Session = Depends(get_db)):
    return db.query(Report).filter_by(org_id=auth.org_id).order_by(Report.created_at.desc()).limit(100).all()
