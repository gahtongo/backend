from datetime import datetime

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "system"
    related_type: str | None = None
    related_id: int | None = None


class NotificationCreate(NotificationBase):
    is_read: bool = False


class NotificationRead(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    related_type: str | None = None
    related_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int = Field(default=0, ge=0)


class NotificationListResponse(BaseModel):
    items: list[NotificationRead]
    unread_count: int = Field(default=0, ge=0)


class NotificationMarkReadResponse(BaseModel):
    success: bool = True
    notification: NotificationRead


class NotificationMarkAllReadResponse(BaseModel):
    success: bool = True
    updated_count: int = Field(default=0, ge=0)