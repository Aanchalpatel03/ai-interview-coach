import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MLLog(Base):
    __tablename__ = "ml_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    interview_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=True)
    model_type: Mapped[str] = mapped_column(String(50))
    output: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


Index("ix_ml_logs_model_type", MLLog.model_type)
Index("ix_ml_logs_created_at", MLLog.created_at)
