import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), unique=True)
    posture_score: Mapped[float] = mapped_column(Float, default=0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0)
    communication_score: Mapped[float] = mapped_column(Float, default=0)
    eye_contact_score: Mapped[float] = mapped_column(Float, default=0)
    hand_movement_score: Mapped[float] = mapped_column(Float, default=0)
    overall_score: Mapped[float] = mapped_column(Float, default=0)
    session_xp: Mapped[int] = mapped_column(default=0)
    improvement_delta: Mapped[float] = mapped_column(Float, default=0)
    suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="feedback")


Index("ix_feedback_created_at", Feedback.created_at)
Index("ix_feedback_overall_score", Feedback.overall_score)
