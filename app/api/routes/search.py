from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.search import AdminSearchResponse
from app.services.search_service import search_admin_content

router = APIRouter(prefix="/admin/search", tags=["Admin Search"])


@router.get("", response_model=AdminSearchResponse)
def admin_search(
    q: str = Query(default="", min_length=0, max_length=120),
    limit_per_group: int = Query(default=6, ge=1, le=10),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin
    return AdminSearchResponse(**search_admin_content(db, q, limit_per_group))