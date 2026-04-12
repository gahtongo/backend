from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
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