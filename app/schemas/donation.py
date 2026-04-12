from pydantic import BaseModel

class DonationCreate(BaseModel):
    donor_name: str | None = None
    donor_email: str | None = None
    amount: int
    currency: str = "NGN"


class DonationResponse(BaseModel):
    id: int
    amount: int
    currency: str
    provider: str
    status: str

    class Config:
        from_attributes = True