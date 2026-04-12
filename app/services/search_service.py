from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.contact_message import ContactMessage
from app.models.news_post import NewsPost
from app.models.report import Report


def search_admin_content(db: Session, query: str, limit_per_group: int = 6) -> dict:
    term = query.strip()
    if not term:
        return {
            "messages": [],
            "reports": [],
            "news": [],
            "campaigns": [],
        }

    safe_limit = max(1, min(limit_per_group, 10))
    like_term = f"%{term}%"

    messages = (
        db.query(ContactMessage)
        .filter(
            or_(
                ContactMessage.name.ilike(like_term),
                ContactMessage.email.ilike(like_term),
                ContactMessage.message.ilike(like_term),
                ContactMessage.status.ilike(like_term),
            )
        )
        .order_by(ContactMessage.created_at.desc(), ContactMessage.id.desc())
        .limit(safe_limit)
        .all()
    )

    reports = (
        db.query(Report)
        .filter(
            or_(
                Report.case_type.ilike(like_term),
                Report.urgency.ilike(like_term),
                Report.description.ilike(like_term),
                Report.location.ilike(like_term),
                Report.reporter_name.ilike(like_term),
                Report.reporter_email.ilike(like_term),
                Report.status.ilike(like_term),
                Report.ai_summary.ilike(like_term),
            )
        )
        .order_by(Report.created_at.desc(), Report.id.desc())
        .limit(safe_limit)
        .all()
    )

    news = (
        db.query(NewsPost)
        .filter(
            or_(
                NewsPost.title.ilike(like_term),
                NewsPost.headline.ilike(like_term),
                NewsPost.excerpt.ilike(like_term),
                NewsPost.content.ilike(like_term),
                NewsPost.category.ilike(like_term),
                NewsPost.status.ilike(like_term),
            )
        )
        .order_by(NewsPost.created_at.desc(), NewsPost.id.desc())
        .limit(safe_limit)
        .all()
    )

    campaigns = (
        db.query(Campaign)
        .filter(
            or_(
                Campaign.title.ilike(like_term),
                Campaign.subtitle.ilike(like_term),
                Campaign.summary.ilike(like_term),
                Campaign.description.ilike(like_term),
                Campaign.status.ilike(like_term),
            )
        )
        .order_by(Campaign.created_at.desc(), Campaign.id.desc())
        .limit(safe_limit)
        .all()
    )

    return {
        "messages": messages,
        "reports": reports,
        "news": news,
        "campaigns": campaigns,
    }