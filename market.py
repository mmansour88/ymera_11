from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float, DateTime, func, ForeignKey
from ..db import Base

class MarketplaceItem(Base):
    __tablename__ = "marketplace_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(String(32), default="0.1.0")
    trust_delta: Mapped[float] = mapped_column(Float, default=0.01)
    created_at = mapped_column(DateTime, server_default=func.now())
