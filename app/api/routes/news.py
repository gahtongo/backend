from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.news_post import NewsPost
from app.schemas.news import (
    NewsPostCreate,
    NewsPostResponse,
    NewsPostUpdate,
    NewsTickerItemResponse,
)
from app.services.news_service import create_news_post, update_news_post

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/public", response_model=list[NewsPostResponse])
def get_public_news(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
):
    return (
        db.query(NewsPost)
        .filter(NewsPost.status == "published")
        .order_by(NewsPost.is_featured.desc(), NewsPost.published_at.desc(), NewsPost.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/ticker", response_model=list[NewsTickerItemResponse])
def get_news_ticker(
    db: Session = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=50),
):
    return (
        db.query(NewsPost)
        .filter(NewsPost.status == "published", NewsPost.show_in_ticker == True)  # noqa: E712
        .order_by(NewsPost.ticker_order.asc(), NewsPost.published_at.desc(), NewsPost.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/public/{slug}", response_model=NewsPostResponse)
def get_public_news_detail(slug: str, db: Session = Depends(get_db)):
    news_post = (
        db.query(NewsPost)
        .filter(NewsPost.slug == slug, NewsPost.status == "published")
        .first()
    )
    if not news_post:
        raise HTTPException(status_code=404, detail="News post not found")
    return news_post


@router.get("/admin/all", response_model=list[NewsPostResponse])
def get_all_news_admin(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    return db.query(NewsPost).order_by(NewsPost.created_at.desc()).all()


@router.post("/admin", response_model=NewsPostResponse, status_code=status.HTTP_201_CREATED)
def create_news_admin(
    payload: NewsPostCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    return create_news_post(db, payload, admin_id=current_admin.id)


@router.put("/admin/{news_id}", response_model=NewsPostResponse)
def update_news_admin(
    news_id: int,
    payload: NewsPostUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    news_post = db.query(NewsPost).filter(NewsPost.id == news_id).first()
    if not news_post:
        raise HTTPException(status_code=404, detail="News post not found")

    return update_news_post(db, news_post, payload)


@router.delete("/admin/{news_id}")
def delete_news_admin(
    news_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    news_post = db.query(NewsPost).filter(NewsPost.id == news_id).first()
    if not news_post:
        raise HTTPException(status_code=404, detail="News post not found")

    db.delete(news_post)
    db.commit()
    return {"message": "News post deleted successfully"}