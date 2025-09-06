
from sqlalchemy.orm import Session

def record_score(db: Session, agent_id: str, skill: str, score: float):
    db.execute("INSERT INTO agent_scores(agent_id, skill, score) VALUES (:a,:s,:c)",
               {"a":agent_id, "s":skill, "c":score})
    db.commit()

def top_teachers(db: Session, skill: str, k: int=3):
    return db.execute("SELECT agent_id, avg(score) as avg FROM agent_scores WHERE skill=:s GROUP BY agent_id ORDER BY avg DESC LIMIT :k",
                      {"s": skill, "k": k}).fetchall()
