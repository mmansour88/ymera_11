
from sqlalchemy.orm import Session
def reward_teacher(db: Session, agent_id: str, points: int, reason: str):
    db.execute("INSERT INTO agent_rewards(agent_id, points, reason) VALUES (:a,:p,:r)", {"a":agent_id,"p":points,"r":reason})
    db.commit()
