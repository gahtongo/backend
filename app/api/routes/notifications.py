from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.notification import (
    NotificationListResponse,
    NotificationMarkAllReadResponse,
    NotificationMarkReadResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import (
    get_unread_count,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

router = APIRouter(prefix="/admin/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin
    items = list_notifications(db, limit=limit)
    unread_count = get_unread_count(db)
    return NotificationListResponse(items=items, unread_count=unread_count)


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def get_notifications_unread_count(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin
    return NotificationUnreadCountResponse(unread_count=get_unread_count(db))


@router.patch("/{notification_id}/read", response_model=NotificationMarkReadResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin
    notification = mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return NotificationMarkReadResponse(success=True, notification=notification)


@router.patch("/mark-all-read", response_model=NotificationMarkAllReadResponse)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin
    updated_count = mark_all_notifications_read(db)
    return NotificationMarkAllReadResponse(success=True, updated_count=updated_count)