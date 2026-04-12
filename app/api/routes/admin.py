from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.report import Report
from app.models.news_post import NewsPost
from app.models.campaign import Campaign
from app.models.site_setting import SiteSetting

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/me")
def get_admin_me(current_admin: AdminUser = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "full_name": current_admin.full_name,
        "email": current_admin.email,
        "role": current_admin.role,
        "is_active": current_admin.is_active,
        "is_superuser": current_admin.is_superuser,
    }


@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    total_admins = db.query(AdminUser).count()
    total_settings = db.query(SiteSetting).count()
    total_reports = db.query(Report).count()
    total_news = db.query(NewsPost).count()
    total_campaigns = db.query(Campaign).count()

    urgent_reports = (
        db.query(Report)
        .filter(Report.urgency.ilike("urgent"))
        .count()
    )

    published_news = (
        db.query(NewsPost)
        .filter(NewsPost.status == "published")
        .count()
    )

    active_campaigns = (
        db.query(Campaign)
        .filter(Campaign.status == "active")
        .count()
    )

    return {
        "message": f"Welcome, {current_admin.full_name}",
        "stats": {
            "total_admins": total_admins,
            "total_settings": total_settings,
            "total_reports": total_reports,
            "urgent_reports": urgent_reports,
            "total_news": total_news,
            "published_news": published_news,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
        },
    }