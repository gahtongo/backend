from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.admin_user import AdminUser

settings = get_settings()


def create_first_superadmin(db: Session) -> None:
    existing_admin = (
        db.query(AdminUser)
        .filter(AdminUser.email == settings.FIRST_SUPERADMIN_EMAIL)
        .first()
    )

    if existing_admin:
        return

    admin = AdminUser(
        full_name="GAHTO Super Admin",
        email=settings.FIRST_SUPERADMIN_EMAIL,
        password_hash=hash_password(settings.FIRST_SUPERADMIN_PASSWORD),
        role="super_admin",
        is_active=True,
        is_superuser=True,
    )
    db.add(admin)
    db.commit()