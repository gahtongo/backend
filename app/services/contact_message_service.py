from sqlalchemy.orm import Session

from app.models.contact_message import ContactMessage
from app.schemas.contact_message import ContactMessageCreate
from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification


VALID_MESSAGE_STATUSES = {"new", "read", "replied", "archived"}


def create_contact_message(db: Session, payload: ContactMessageCreate) -> ContactMessage:
    message = ContactMessage(
        name=payload.name.strip(),
        email=str(payload.email).strip().lower(),
        message=payload.message.strip(),
        status="new",
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    preview = message.message.strip()
    if len(preview) > 140:
        preview = f"{preview[:137]}..."

    create_notification(
        db,
        NotificationCreate(
            title="New contact message received",
            message=f"{message.name} ({message.email}) sent a new message: {preview}",
            type="contact_message",
            related_type="contact_message",
            related_id=message.id,
            is_read=False,
        ),
    )

    return message


def update_contact_message_status(
    db: Session,
    contact_message: ContactMessage,
    status: str,
) -> ContactMessage:
    normalized_status = status.strip().lower()

    if normalized_status not in VALID_MESSAGE_STATUSES:
        raise ValueError("Invalid status")

    contact_message.status = normalized_status
    db.commit()
    db.refresh(contact_message)
    return contact_message