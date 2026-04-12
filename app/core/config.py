from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GAHTO Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = "sqlite:///./gahto.db"

    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    FIRST_SUPERADMIN_EMAIL: str = "admin@gahto.org"
    FIRST_SUPERADMIN_PASSWORD: str = "@Admingahto1"

    MEDIA_UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 20

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "GAHTO"

    OPENAI_API_KEY: str = ""
    AI_CHAT_MODEL: str = "gpt-5.4"
    AI_OPTIMIZER_MODEL: str = "gpt-5.4"

    # ✅ ADD THESE PROPERLY HERE
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:3000"

    WHATSAPP_PROVIDER: str = ""
    WHATSAPP_API_KEY: str = ""
    WHATSAPP_SENDER_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.BACKEND_CORS_ORIGINS.strip():
            return []
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()