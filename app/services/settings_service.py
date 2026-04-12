from sqlalchemy.orm import Session

from app.models.site_setting import SiteSetting


DEFAULT_PUBLIC_SETTINGS = [
    {
        "key": "whatsapp_number",
        "value": "+2340000000000",
        "description": "Primary WhatsApp contact line",
        "is_public": True,
    },
    {
        "key": "emergency_phone",
        "value": "+2340000000000",
        "description": "Emergency reporting phone number",
        "is_public": True,
    },
    {
        "key": "nigeria_office_phone",
        "value": "+2340000000000",
        "description": "Nigeria office phone line",
        "is_public": True,
    },
    {
        "key": "mali_office_phone",
        "value": "+22300000000",
        "description": "Mali office phone line",
        "is_public": True,
    },
    {
        "key": "support_email",
        "value": "info@gahto.org",
        "description": "Support email address",
        "is_public": True,
    },
    {
        "key": "facebook_url",
        "value": "https://facebook.com/",
        "description": "Official Facebook page",
        "is_public": True,
    },
    {
        "key": "twitter_url",
        "value": "https://x.com/",
        "description": "Official Twitter/X page",
        "is_public": True,
    },
]


def seed_default_site_settings(db: Session) -> None:
    for item in DEFAULT_PUBLIC_SETTINGS:
        existing = db.query(SiteSetting).filter(SiteSetting.key == item["key"]).first()
        if existing:
            continue

        db.add(
            SiteSetting(
                key=item["key"],
                value=item["value"],
                description=item["description"],
                is_public=item["is_public"],
            )
        )

    db.commit()