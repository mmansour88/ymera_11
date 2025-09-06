from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from .db import get_db
from .models import Task
router = APIRouter(prefix="/tasks", tags=["tasks"])
class TaskIn(BaseModel):
    title:str; description:str; team_id:int|None=None
@router.post("")
def create_task(payload: TaskIn, db: Session = Depends(get_db)):
    t=Task(title=payload.title, description=payload.description, team_id=payload.team_id, status="queued", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(t); db.flush()
    return {"id":t.id}
@router.get("")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).all()
