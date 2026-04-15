from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    case_type: Mapped[str] = mapped_column(String(120), nullable=False, default="Suspected Trafficking")
    urgency: Mapped[str] = mapped_column(String(50), nullable=False, default="Urgent")
    description: Mapped[str] = mapped_column(Text, nullable=False)

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    incident_time: Mapped[str | None] = mapped_column(String(255), nullable=True)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reporter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_phone: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    ai_severity_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalation_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )