import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    __table_args__ = (UniqueConstraint("date", "type", name="uq_daily_challenges_date_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[date] = mapped_column(Date, index=True)
    question: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(32), index=True)
    xp_reward: Mapped[int] = mapped_column(Integer, default=25)

    progress = relationship("UserProgress", back_populates="challenge", cascade="all, delete-orphan")


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_user_progress_user_challenge"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("daily_challenges.id", ondelete="CASCADE"), index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="challenge_progress")
    challenge = relationship("DailyChallenge", back_populates="progress")
