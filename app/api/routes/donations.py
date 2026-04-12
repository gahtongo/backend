from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.donation import DonationCreate
from app.services.donation_service import initialize_paystack_payment

router = APIRouter(prefix="/donations", tags=["Donations"])


@router.post("/paystack/initialize")
def paystack_initialize(data: DonationCreate, db: Session = Depends(get_db)):
    url = initialize_paystack_payment(db, data)
    return {"payment_url": url}