from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)

    donor_name = Column(String, nullable=True)
    donor_email = Column(String, nullable=True)

    amount = Column(Integer, nullable=False)
    currency = Column(String, default="NGN")

    provider = Column(String)  # paystack / stripe
    status = Column(String, default="pending")

    provider_reference = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())