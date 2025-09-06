from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import get_db
from .models import Agent
router = APIRouter(prefix="/agents", tags=["agents"])
class AgentIn(BaseModel):
    name:str; specialization:str; team_id:int|None=None
@router.get("")
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()
@router.post("")
def create_agent(payload: AgentIn, db: Session = Depends(get_db)):
    if db.query(Agent).filter(Agent.name==payload.name).first():
        raise HTTPException(400,"Agent name exists")
    a=Agent(name=payload.name, specialization=payload.specialization, team_id=payload.team_id, active=True)
    db.add(a); db.flush()
    return {"id":a.id,"name":a.name}
