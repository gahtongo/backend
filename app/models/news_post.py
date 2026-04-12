from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NewsPost(Base):
    __tablename__ = "news_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[str] = mapped_column(String(100), default="general", nullable=False)
    featured_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    external_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_in_ticker: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ticker_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_by_admin_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )