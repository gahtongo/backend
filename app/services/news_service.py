from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.news_post import NewsPost
from app.schemas.news import NewsPostCreate, NewsPostUpdate
from app.services.slug_service import ensure_unique_slug, slugify


def generate_news_slug(db: Session, title: str, explicit_slug: str | None = None) -> str:
    raw_slug = explicit_slug or title
    base_slug = slugify(raw_slug)
    if not base_slug:
        base_slug = "news-post"

    existing_slugs = {row[0] for row in db.query(NewsPost.slug).all()}
    return ensure_unique_slug(base_slug, existing_slugs)


def create_news_post(
    db: Session,
    payload: NewsPostCreate,
    admin_id: int | None = None,
) -> NewsPost:
    slug = generate_news_slug(db, payload.title, payload.slug)

    published_at = None
    if payload.status.lower() == "published":
        published_at = datetime.now(timezone.utc).replace(tzinfo=None)

    news_post = NewsPost(
        title=payload.title,
        slug=slug,
        headline=payload.headline,
        excerpt=payload.excerpt,
        content=payload.content,
        category=payload.category,
        featured_image_url=payload.featured_image_url,
        video_url=payload.video_url,
        external_link=payload.external_link,
        is_featured=payload.is_featured,
        show_in_ticker=payload.show_in_ticker,
        ticker_order=payload.ticker_order,
        status=payload.status.lower(),
        published_at=published_at,
        created_by_admin_id=admin_id,
    )
    db.add(news_post)
    db.commit()
    db.refresh(news_post)
    return news_post


def update_news_post(db: Session, news_post: NewsPost, payload: NewsPostUpdate) -> NewsPost:
    data = payload.model_dump(exclude_unset=True)

    if "slug" in data and data["slug"]:
        proposed_slug = slugify(data["slug"])
        existing_slugs = {
            row[0]
            for row in db.query(NewsPost.slug).filter(NewsPost.id != news_post.id).all()
        }
        data["slug"] = ensure_unique_slug(proposed_slug or "news-post", existing_slugs)

    elif "title" in data and data["title"]:
        current_base = slugify(news_post.title)
        if news_post.slug == current_base:
            existing_slugs = {
                row[0]
                for row in db.query(NewsPost.slug).filter(NewsPost.id != news_post.id).all()
            }
            data["slug"] = ensure_unique_slug(slugify(data["title"]) or "news-post", existing_slugs)

    if "status" in data and data["status"]:
        data["status"] = data["status"].lower()
        if data["status"] == "published" and news_post.published_at is None:
            data["published_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    for field, value in data.items():
        setattr(news_post, field, value)

    db.commit()
    db.refresh(news_post)
    return news_post