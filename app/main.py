from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.admin import router as admin_router
from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.contact_messages import router as contact_messages_router
from app.api.routes.news import router as news_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.reports import router as reports_router
from app.api.routes.search import router as search_router
from app.api.routes.settings import router as settings_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine

from app.models.admin_user import AdminUser  # noqa: F401
from app.models.campaign import Campaign  # noqa: F401
from app.models.contact_message import ContactMessage  # noqa: F401
from app.models.news_post import NewsPost  # noqa: F401
from app.models.notification_log import NotificationLog  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.site_setting import SiteSetting  # noqa: F401
from app.services.bootstrap_service import create_first_superadmin
from app.services.settings_service import seed_default_site_settings
from app.api.routes import donations


settings = get_settings()

# ✅ FIX: Ensure uploads directory exists BEFORE mounting
upload_dir = Path(settings.MEDIA_UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(news_router, prefix=settings.API_V1_PREFIX)
app.include_router(campaigns_router, prefix=settings.API_V1_PREFIX)
app.include_router(contact_messages_router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications_router, prefix=settings.API_V1_PREFIX)
app.include_router(search_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
app.include_router(donations.router, prefix="/api/v1")

# ✅ SAFE mount (directory now guaranteed to exist)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.on_event("startup")
def on_startup():
    # (kept for redundancy, harmless and safe)
    Path(settings.MEDIA_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        create_first_superadmin(db)
        seed_default_site_settings(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "GAHTO backend is running",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}