from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.market import MarketplaceItem
from ..models.collab import Agent

router = APIRouter()

@router.post("/market/publish")
def publish(author_agent_id: int, name: str, description: str, version: str = "0.1.0", db: Session = Depends(get_db)):
    if not db.query(Agent).get(author_agent_id):
        raise HTTPException(404, "Author agent not found")
    item = MarketplaceItem(author_agent_id=author_agent_id, name=name, description=description, version=version)
    db.add(item)
    ag = db.query(Agent).get(author_agent_id); ag.reward_points += 10; ag.trust += 0.01
    db.commit()
    return {"id": item.id, "reward_points": ag.reward_points, "trust": ag.trust}

@router.get("/market/list")
def list_items(db: Session = Depends(get_db)):
    return [{"id": i.id, "name": i.name, "version": i.version} for i in db.query(MarketplaceItem).all()]
