from datetime import datetime

from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    description: str = Field(min_length=10)
    image_url: str | None = Field(default=None, max_length=500)
    donation_link: str | None = Field(default=None, max_length=500)
    volunteer_link: str | None = Field(default=None, max_length=500)
    status: str = Field(default="draft", max_length=50)
    display_order: int = 0
    is_featured: bool = False
    start_date: datetime | None = None
    end_date: datetime | None = None


class CampaignCreate(CampaignBase):
    slug: str | None = None


class CampaignUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    description: str | None = Field(default=None, min_length=10)
    image_url: str | None = Field(default=None, max_length=500)
    donation_link: str | None = Field(default=None, max_length=500)
    volunteer_link: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, max_length=50)
    display_order: int | None = None
    is_featured: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    slug: str | None = None


class CampaignResponse(BaseModel):
    id: int
    title: str
    slug: str
    subtitle: str | None = None
    summary: str | None = None
    description: str
    image_url: str | None = None
    donation_link: str | None = None
    volunteer_link: str | None = None
    status: str
    display_order: int
    is_featured: bool
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True