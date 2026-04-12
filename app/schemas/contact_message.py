from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    message: str = Field(min_length=5, max_length=5000)


class ContactMessageUpdateStatus(BaseModel):
    status: str = Field(min_length=2, max_length=50)


class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True