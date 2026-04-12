from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.site_setting import SiteSetting
from app.schemas.settings import (
    SiteSettingCreate,
    SiteSettingUpdate,
    SiteSettingResponse,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


# 🔓 PUBLIC SETTINGS
@router.get("/public", response_model=list[SiteSettingResponse])
def get_public_settings(db: Session = Depends(get_db)):
    return (
        db.query(SiteSetting)
        .filter(SiteSetting.is_public == True)
        .order_by(SiteSetting.key.asc())
        .all()
    )


# 🔐 ADMIN: GET ALL SETTINGS
@router.get("/admin", response_model=list[SiteSettingResponse])
def get_all_settings(db: Session = Depends(get_db)):
    return db.query(SiteSetting).order_by(SiteSetting.key.asc()).all()


# 🔐 ADMIN: CREATE SETTING
@router.post("/admin", response_model=SiteSettingResponse)
def create_setting(payload: SiteSettingCreate, db: Session = Depends(get_db)):
    existing = db.query(SiteSetting).filter_by(key=payload.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Key already exists")

    setting = SiteSetting(
        key=payload.key,
        value=payload.value,
        description=payload.description,
        is_public=payload.is_public,
    )

    db.add(setting)
    db.commit()
    db.refresh(setting)

    return setting


# 🔐 ADMIN: UPDATE SETTING
@router.put("/admin/{key}", response_model=SiteSettingResponse)
def update_setting(
    key: str, payload: SiteSettingUpdate, db: Session = Depends(get_db)
):
    setting = db.query(SiteSetting).filter_by(key=key).first()

    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    if payload.value is not None:
        setting.value = payload.value

    if payload.description is not None:
        setting.description = payload.description

    if payload.is_public is not None:
        setting.is_public = payload.is_public

    db.commit()
    db.refresh(setting)

    return setting