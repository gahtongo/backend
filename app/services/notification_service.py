from sqlalchemy.orm import Session

from app.models.notification_log import NotificationLog
from app.schemas.notification import NotificationCreate


def create_notification(db: Session, payload: NotificationCreate) -> NotificationLog:
    notification = NotificationLog(
        title=payload.title,
        message=payload.message,
        type=payload.type,
        is_read=payload.is_read,
        related_type=payload.related_type,
        related_id=payload.related_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, limit: int = 10) -> list[NotificationLog]:
    safe_limit = max(1, min(limit, 50))
    return (
        db.query(NotificationLog)
        .order_by(NotificationLog.created_at.desc(), NotificationLog.id.desc())
        .limit(safe_limit)
        .all()
    )


def get_unread_count(db: Session) -> int:
    return db.query(NotificationLog).filter(NotificationLog.is_read.is_(False)).count()


def mark_notification_read(db: Session, notification_id: int) -> NotificationLog | None:
    notification = (
        db.query(NotificationLog)
        .filter(NotificationLog.id == notification_id)
        .first()
    )
    if not notification:
        return None

    if not notification.is_read:
        notification.is_read = True
        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_read(db: Session) -> int:
    unread_items = (
        db.query(NotificationLog)
        .filter(NotificationLog.is_read.is_(False))
        .all()
    )

    if not unread_items:
        return 0

    for item in unread_items:
        item.is_read = True

    db.commit()
    return len(unread_items)