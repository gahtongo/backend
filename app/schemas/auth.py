from pydantic import BaseModel, EmailStr, Field


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_link: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str