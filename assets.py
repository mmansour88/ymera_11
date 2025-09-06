from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, LargeBinary
from ..db import Base

class FileAsset(Base):
    __tablename__ = "file_assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    mime: Mapped[str] = mapped_column(String(128), default="application/octet-stream")
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_at = mapped_column(DateTime, server_default=func.now())
