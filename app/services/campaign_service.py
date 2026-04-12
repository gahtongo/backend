from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.services.slug_service import ensure_unique_slug, slugify


def generate_campaign_slug(db: Session, title: str, explicit_slug: str | None = None) -> str:
    raw_slug = explicit_slug or title
    base_slug = slugify(raw_slug)
    if not base_slug:
        base_slug = "campaign"

    existing_slugs = {row[0] for row in db.query(Campaign.slug).all()}
    return ensure_unique_slug(base_slug, existing_slugs)


def create_campaign(db: Session, payload: CampaignCreate) -> Campaign:
    slug = generate_campaign_slug(db, payload.title, payload.slug)

    campaign = Campaign(
        title=payload.title,
        slug=slug,
        subtitle=payload.subtitle,
        summary=payload.summary,
        description=payload.description,
        image_url=payload.image_url,
        donation_link=payload.donation_link,
        volunteer_link=payload.volunteer_link,
        status=payload.status.lower(),
        display_order=payload.display_order,
        is_featured=payload.is_featured,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def update_campaign(db: Session, campaign: Campaign, payload: CampaignUpdate) -> Campaign:
    data = payload.model_dump(exclude_unset=True)

    if "slug" in data and data["slug"]:
        proposed_slug = slugify(data["slug"])
        existing_slugs = {
            row[0]
            for row in db.query(Campaign.slug).filter(Campaign.id != campaign.id).all()
        }
        data["slug"] = ensure_unique_slug(proposed_slug or "campaign", existing_slugs)

    elif "title" in data and data["title"]:
        current_base = slugify(campaign.title)
        if campaign.slug == current_base:
            existing_slugs = {
                row[0]
                for row in db.query(Campaign.slug).filter(Campaign.id != campaign.id).all()
            }
            data["slug"] = ensure_unique_slug(slugify(data["title"]) or "campaign", existing_slugs)

    if "status" in data and data["status"]:
        data["status"] = data["status"].lower()

    for field, value in data.items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign