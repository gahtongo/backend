import requests
from sqlalchemy.orm import Session
from app.models.donation import Donation
from app.core.config import get_settings

# ---------------- PAYSTACK INIT ---------------- #

def initialize_paystack_payment(db: Session, data):
    donation = Donation(
        donor_name=data.donor_name,
        donor_email=data.donor_email,
        amount=data.amount,
        currency=data.currency,
        provider="paystack",
        status="pending"
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": data.donor_email or "anonymous@gahto.org",
        "amount": data.amount * 100,  # Paystack uses kobo
        "callback_url": f"{settings.FRONTEND_URL}/donate/success"
    }

    response = requests.post(url, json=payload, headers=headers)
    res_data = response.json()

    donation.provider_reference = res_data["data"]["reference"]
    db.commit()

    return res_data["data"]["authorization_url"]