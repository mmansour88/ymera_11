from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Text
from ..db import Base

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(200), index=True)
    desc: Mapped[str] = mapped_column(Text, default="")
    created_at = mapped_column(DateTime, server_default=func.now())
