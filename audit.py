
from datetime import datetime
from sqlalchemy.orm import Session

def record_event(db: Session, org_id: int, actor: str, action: str, meta: dict):
    db.execute(
        "INSERT INTO audit_log(org_id, actor, action, meta, created_at) VALUES (:o,:a,:ac,:m,:t)",
        {"o": org_id, "a": actor, "ac": action, "m": str(meta), "t": datetime.utcnow()}
    )
    db.commit()
