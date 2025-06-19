# app/modules/auth/schemas/email.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationResponse(BaseModel):
    success: bool
    message: str
    expires_in_hours: Optional[int] = None


class EmailVerifyTokenRequest(BaseModel):
    token: str


class EmailVerifyTokenResponse(BaseModel):
    success: bool
    message: str
    email_verified: bool = False
    user_id: Optional[int] = None


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class EmailStatusResponse(BaseModel):
    email_configured: bool
    smtp_available: bool
    templates_available: bool
    rate_limiting_enabled: bool