import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    total_score: Mapped[float] = mapped_column(Float, default=0)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(32), default="Beginner")
    xp_points: Mapped[int] = mapped_column(Integer, default=0)
    badges: Mapped[str | None] = mapped_column(Text, nullable=True)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    improvement_score: Mapped[float] = mapped_column(Float, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="leaderboard")
