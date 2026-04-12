import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import (
    AdminLoginRequest,
    TokenResponse,
    AdminUserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
def login_admin(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.email == payload.email).first()

    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    token = create_access_token(subject=admin.id)
    return TokenResponse(access_token=token)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AdminUser:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    admin = db.query(AdminUser).filter(AdminUser.id == int(admin_id)).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    return admin


@router.get("/me", response_model=AdminUserResponse)
def get_logged_in_admin(current_admin: AdminUser = Depends(get_current_admin)):
    return current_admin


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.email == payload.email).first()

    generic_message = "If the account exists, a password reset link has been generated."

    if not admin or not admin.is_active:
        return ForgotPasswordResponse(message=generic_message)

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    admin.reset_token = token
    admin.reset_token_expires_at = expires_at
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/admin/reset-password?token={token}"

    print("\n" + "=" * 80)
    print("GAHTO ADMIN PASSWORD RESET LINK")
    print(reset_link)
    print("=" * 80 + "\n")

    return ForgotPasswordResponse(
        message=generic_message,
        reset_link=reset_link,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.reset_token == payload.token).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if not admin.reset_token_expires_at or admin.reset_token_expires_at < datetime.utcnow():
        admin.reset_token = None
        admin.reset_token_expires_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    admin.password_hash = hash_password(payload.new_password)
    admin.reset_token = None
    admin.reset_token_expires_at = None
    db.commit()

    return MessageResponse(message="Password has been reset successfully")