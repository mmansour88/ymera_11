from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, String, ForeignKey
from ..db import Base

class AgentScore(Base):
    __tablename__ = "agent_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"))
    task_type: Mapped[str] = mapped_column(String(64))
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    samples: Mapped[int] = mapped_column(Integer, default=0)
