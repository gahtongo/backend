from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.services.campaign_service import create_campaign, update_campaign

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("/public", response_model=list[CampaignResponse])
def get_public_campaigns(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
):
    return (
        db.query(Campaign)
        .filter(Campaign.status == "active")
        .order_by(Campaign.is_featured.desc(), Campaign.display_order.asc(), Campaign.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/public/{slug}", response_model=CampaignResponse)
def get_public_campaign_detail(slug: str, db: Session = Depends(get_db)):
    campaign = (
        db.query(Campaign)
        .filter(Campaign.slug == slug, Campaign.status == "active")
        .first()
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/admin/all", response_model=list[CampaignResponse])
def get_all_campaigns_admin(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    return (
        db.query(Campaign)
        .order_by(Campaign.display_order.asc(), Campaign.created_at.desc())
        .all()
    )


@router.post("/admin", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign_admin(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    return create_campaign(db, payload)


@router.put("/admin/{campaign_id}", response_model=CampaignResponse)
def update_campaign_admin(
    campaign_id: int,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return update_campaign(db, campaign, payload)


@router.delete("/admin/{campaign_id}")
def delete_campaign_admin(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return {"message": "Campaign deleted successfully"}