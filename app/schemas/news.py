from datetime import datetime

from pydantic import BaseModel, Field


class NewsPostBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    headline: str | None = Field(default=None, max_length=255)
    excerpt: str | None = None
    content: str = Field(min_length=10)
    category: str = Field(default="general", max_length=100)
    featured_image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    external_link: str | None = Field(default=None, max_length=500)
    is_featured: bool = False
    show_in_ticker: bool = False
    ticker_order: int = 0
    status: str = Field(default="draft", max_length=50)


class NewsPostCreate(NewsPostBase):
    slug: str | None = None


class NewsPostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    headline: str | None = Field(default=None, max_length=255)
    excerpt: str | None = None
    content: str | None = Field(default=None, min_length=10)
    category: str | None = Field(default=None, max_length=100)
    featured_image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    external_link: str | None = Field(default=None, max_length=500)
    is_featured: bool | None = None
    show_in_ticker: bool | None = None
    ticker_order: int | None = None
    status: str | None = Field(default=None, max_length=50)
    slug: str | None = None


class NewsPostResponse(BaseModel):
    id: int
    title: str
    slug: str
    headline: str | None = None
    excerpt: str | None = None
    content: str
    category: str
    featured_image_url: str | None = None
    video_url: str | None = None
    external_link: str | None = None
    is_featured: bool
    show_in_ticker: bool
    ticker_order: int
    status: str
    published_at: datetime | None = None
    created_by_admin_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsTickerItemResponse(BaseModel):
    id: int
    title: str
    slug: str
    headline: str | None = None
    category: str
    featured_image_url: str | None = None
    video_url: str | None = None
    external_link: str | None = None
    ticker_order: int
    published_at: datetime | None = None

    class Config:
        from_attributes = True