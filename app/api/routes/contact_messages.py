from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.contact_message import ContactMessage
from app.schemas.contact_message import (
    ContactMessageCreate,
    ContactMessageResponse,
    ContactMessageUpdateStatus,
)
from app.services.contact_message_service import (
    create_contact_message,
    update_contact_message_status,
)

router = APIRouter(prefix="/contact-messages", tags=["Contact Messages"])


@router.post(
    "",
    response_model=ContactMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_contact_message(
    payload: ContactMessageCreate,
    db: Session = Depends(get_db),
):
    return create_contact_message(db, payload)


@router.get("/admin", response_model=list[ContactMessageResponse])
def get_contact_messages_admin(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
    status_filter: str | None = Query(default=None),
):
    _ = current_admin

    query = db.query(ContactMessage)

    if status_filter:
        query = query.filter(ContactMessage.status == status_filter.strip().lower())

    return query.order_by(ContactMessage.created_at.desc()).all()


@router.put("/admin/{message_id}", response_model=ContactMessageResponse)
def update_contact_message_admin(
    message_id: int,
    payload: ContactMessageUpdateStatus,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    _ = current_admin

    contact_message = (
        db.query(ContactMessage)
        .filter(ContactMessage.id == message_id)
        .first()
    )

    if not contact_message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        return update_contact_message_status(db, contact_message, payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid message status")