# app/config/settings.py
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProzLab Backend API"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "prozlab_db"
    DB_USER: str = "proz_user"
    DB_PASSWORD: str = "Root#2022"
    DATABASE_URL: Optional[str] = None

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    MAIL_SUPPORT: Optional[str] = None

    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # OTP
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6
    MAX_OTP_ATTEMPTS: int = 3

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Verification
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5_242_880
    ALLOWED_IMAGE_TYPES: List[str] = ["jpg", "jpeg", "png", "gif"]
    STORAGE_TYPE: str = "local"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator("ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def _split_image_types(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    @property
    def allowed_image_types(self) -> List[str]:
        # split it on commas at runtime
        return [s.strip() for s in self.ALLOWED_IMAGE_TYPES.split(",") if s.strip()]

    @property
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

    def is_sms_enabled(self) -> bool:
        return all([self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN, self.TWILIO_PHONE_NUMBER])

    def is_email_enabled(self) -> bool:
        return all([self.SMTP_HOST, self.SMTP_PORT, self.SMTP_USER, self.SMTP_PASSWORD, self.EMAIL_FROM])

# at the very bottom:
settings = Settings()
