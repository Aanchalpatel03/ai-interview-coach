import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(32), default="active")
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="mid")

    user = relationship("User", back_populates="interviews")
    responses = relationship("Response", back_populates="interview", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="interview", uselist=False, cascade="all, delete-orphan")
