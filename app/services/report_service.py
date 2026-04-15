from sqlalchemy.orm import Session

from app.models.report import Report
from app.schemas.notification import NotificationCreate
from app.schemas.report import ReportCreate, ReportUpdateAdmin

from app.services.notification_service import create_notification
from app.services.ai_triage_service import generate_support_reply, AIChatRequest
from app.schemas.ai import AIChatMessage


VALID_REPORT_STATUSES = {"new", "in_review", "resolved", "archived"}
VALID_ESCALATION_STATUSES = {"pending", "under_review", "escalated", "closed"}
VALID_URGENCY_LEVELS = {"low", "medium", "urgent"}


def create_report(db: Session, payload: ReportCreate) -> Report:
    normalized_urgency = payload.urgency.strip().lower()
    if normalized_urgency not in VALID_URGENCY_LEVELS:
        normalized_urgency = "urgent"

    urgency_value = normalized_urgency.capitalize()

    reporter_name = None if payload.is_anonymous else _clean_optional(payload.reporter_name)
    reporter_email = None if payload.is_anonymous else _clean_optional(payload.reporter_email)
    reporter_phone = None if payload.is_anonymous else _clean_optional(payload.reporter_phone)

    report = Report(
        case_type=payload.case_type.strip(),
        urgency=urgency_value,
        description=payload.description.strip(),
        location=_clean_optional(payload.location),
        incident_time=_clean_optional(payload.incident_time),
        additional_notes=_clean_optional(payload.additional_notes),
        evidence_url=_clean_optional(payload.evidence_url),
        is_anonymous=payload.is_anonymous,
        reporter_name=reporter_name,
        reporter_email=reporter_email,
        reporter_phone=reporter_phone,
        status="new",
        ai_severity_score=None,
        ai_summary=None,
        escalation_status="pending",
    )


    db.add(report)
    db.commit()
    db.refresh(report)

    # --- AI triage automation ---
    try:
        ai_request = AIChatRequest(messages=[AIChatMessage(role="user", content=report.description)])
        ai_response = generate_support_reply(ai_request)
        # Map risk_level to a numeric severity score
        risk_map = {"high": 90, "elevated": 60, "normal": 20}
        report.ai_severity_score = risk_map.get(ai_response.risk_level, 20)
        report.ai_summary = ai_response.reply
        db.commit()
        db.refresh(report)
    except Exception as e:
        # Log or ignore AI errors, but don't block report creation
        pass

    preview = report.description.strip()
    if len(preview) > 140:
        preview = f"{preview[:137]}..."

    title = "Urgent report submitted" if report.urgency.lower() == "urgent" else "New report submitted"
    reporter_label = "Anonymous reporter" if report.is_anonymous else (report.reporter_name or report.reporter_email or "Identified reporter")

    create_notification(
        db,
        NotificationCreate(
            title=title,
            message=f"{reporter_label} submitted a {report.case_type.lower()} report: {preview}",
            type="report",
            related_type="report",
            related_id=report.id,
            is_read=False,
        ),
    )

    return report


def list_reports(
    db: Session,
    status_filter: str | None = None,
    urgency_filter: str | None = None,
    escalation_filter: str | None = None,
) -> list[Report]:
    query = db.query(Report)

    if status_filter:
        query = query.filter(Report.status == status_filter.strip().lower())

    if urgency_filter:
        query = query.filter(Report.urgency == urgency_filter.strip().capitalize())

    if escalation_filter:
        query = query.filter(Report.escalation_status == escalation_filter.strip().lower())

    return query.order_by(Report.created_at.desc(), Report.id.desc()).all()


def update_report_admin(db: Session, report: Report, payload: ReportUpdateAdmin) -> Report:
    if payload.status is not None:
        normalized_status = payload.status.strip().lower()
        if normalized_status not in VALID_REPORT_STATUSES:
            raise ValueError("Invalid report status")
        report.status = normalized_status

    if payload.escalation_status is not None:
        normalized_escalation = payload.escalation_status.strip().lower()
        if normalized_escalation not in VALID_ESCALATION_STATUSES:
            raise ValueError("Invalid escalation status")
        report.escalation_status = normalized_escalation

    if payload.ai_severity_score is not None:
        report.ai_severity_score = payload.ai_severity_score

    if payload.ai_summary is not None:
        report.ai_summary = payload.ai_summary.strip() or None

    db.commit()
    db.refresh(report)
    return report


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None