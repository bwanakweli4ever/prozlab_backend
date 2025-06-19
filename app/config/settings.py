# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "ProzLab Backend API"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "prozlab_db"
    DB_USER: str = "proz_user"
    DB_PASSWORD: str = "Root#2022"
    DATABASE_URL: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    # Twilio SMS Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6
    MAX_OTP_ATTEMPTS: int = 3
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Verification settings
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def get_database_url(self) -> str:
        """Get the database URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def is_sms_enabled(self) -> bool:
        """Check if SMS/Twilio is properly configured"""
        return all([
            self.TWILIO_ACCOUNT_SID,
            self.TWILIO_AUTH_TOKEN,
            self.TWILIO_PHONE_NUMBER
        ])
    
    def is_email_enabled(self) -> bool:
        """Check if email/SMTP is properly configured"""
        return all([
            self.SMTP_HOST,
            self.SMTP_PORT,
            self.SMTP_USER,
            self.SMTP_PASSWORD,
            self.EMAIL_FROM
        ])


settings = Settings()