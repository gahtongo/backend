from datetime import datetime

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    case_type: str = Field(default="Suspected Trafficking", min_length=2, max_length=120)
    urgency: str = Field(default="Urgent", min_length=2, max_length=50)
    description: str = Field(min_length=10)

    location: str | None = Field(default=None, max_length=255)
    incident_time: str | None = Field(default=None, max_length=255)
    additional_notes: str | None = None
    evidence_url: str | None = Field(default=None, max_length=1024)

    is_anonymous: bool = True
    reporter_name: str | None = Field(default=None, max_length=255)
    reporter_email: str | None = Field(default=None, max_length=255)
    reporter_phone: str | None = Field(default=None, max_length=100)


class ReportUpdateAdmin(BaseModel):
    status: str | None = Field(default=None, max_length=50)
    escalation_status: str | None = Field(default=None, max_length=50)
    ai_severity_score: int | None = Field(default=None, ge=0, le=100)
    ai_summary: str | None = None


class ReportResponse(BaseModel):
    id: int
    case_type: str
    urgency: str
    description: str

    location: str | None = None
    incident_time: str | None = None
    additional_notes: str | None = None
    evidence_url: str | None = None

    is_anonymous: bool
    reporter_name: str | None = None
    reporter_email: str | None = None
    reporter_phone: str | None = None

    status: str
    ai_severity_score: int | None = None
    ai_summary: str | None = None
    escalation_status: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True