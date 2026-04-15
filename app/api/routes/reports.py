from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.core.config import settings
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse, ReportUpdateAdmin
from app.services.report_service import create_report, list_reports, update_report_admin

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
):
    return create_report(db, payload)


@router.post(
    "/submit",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_report_with_evidence(
    case_type: str = Form("Suspected Trafficking"),
    urgency: str = Form("Urgent"),
    description: str = Form(...),
    location: str | None = Form(None),
    incident_time: str | None = Form(None),
    additional_notes: str | None = Form(None),
    is_anonymous: bool = Form(True),
    reporter_name: str | None = Form(None),
    reporter_email: str | None = Form(None),
    reporter_phone: str | None = Form(None),
    evidence_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    evidence_url = None
    if evidence_file is not None:
        filename = f"{uuid4().hex}_{Path(evidence_file.filename).name}"
        upload_path = Path(settings.MEDIA_UPLOAD_DIR) / filename
        with upload_path.open("wb") as buffer:
            buffer.write(await evidence_file.read())
        evidence_url = f"/uploads/{filename}"

    payload = ReportCreate(
        case_type=case_type,
        urgency=urgency,
        description=description,
        location=location,
        incident_time=incident_time,
        additional_notes=additional_notes,
        is_anonymous=is_anonymous,
        reporter_name=reporter_name,
        reporter_email=reporter_email,
        reporter_phone=reporter_phone,
        evidence_url=evidence_url,
    )

    return create_report(db, payload)


@router.get("/admin", response_model=list[ReportResponse])
def get_reports_admin(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
    status_filter: str | None = Query(default=None),
    urgency_filter: str | None = Query(default=None),
    escalation_filter: str | None = Query(default=None),
):
    _ = current_admin
    return list_reports(
        db=db,
        status_filter=status_filter,
        urgency_filter=urgency_filter,
        escalation_filter=escalation_filter,
    )


@router.get("/admin/{report_id}", response_model=ReportResponse)
def get_single_report_admin(
    report_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.put("/admin/{report_id}", response_model=ReportResponse)
def update_report_admin_route(
    report_id: int,
    payload: ReportUpdateAdmin,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        return update_report_admin(db, report, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))