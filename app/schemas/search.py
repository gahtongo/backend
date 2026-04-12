from datetime import datetime

from pydantic import BaseModel


class SearchNewsItem(BaseModel):
    id: int
    title: str
    headline: str | None = None
    excerpt: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchCampaignItem(BaseModel):
    id: int
    title: str
    subtitle: str | None = None
    summary: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchMessageItem(BaseModel):
    id: int
    name: str
    email: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SearchReportItem(BaseModel):
    id: int
    case_type: str
    urgency: str
    description: str
    location: str | None = None
    reporter_name: str | None = None
    reporter_email: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminSearchResponse(BaseModel):
    messages: list[SearchMessageItem]
    reports: list[SearchReportItem]
    news: list[SearchNewsItem]
    campaigns: list[SearchCampaignItem]