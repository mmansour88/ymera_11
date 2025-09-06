
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth.rbac import require_scope, TokenPayload
from ..db import get_db
from ..models import WebhookSubscriber

router = APIRouter()

class Subscribe(BaseModel):
    topic: str
    url: str
    secret: str | None = None

@router.post("/subscribe")
def subscribe(body: Subscribe, auth: TokenPayload = Depends(require_scope("webhooks:manage")), db: Session = Depends(get_db)):
    sub = WebhookSubscriber(org_id=auth.org_id, topic=body.topic, url=body.url, secret=body.secret, active=True)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@router.get("/list")
def list_subs(auth: TokenPayload = Depends(require_scope("webhooks:manage")), db: Session = Depends(get_db)):
    return db.query(WebhookSubscriber).filter_by(org_id=auth.org_id).all()
