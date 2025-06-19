from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from app.database.base_class import Base


class OTPVerification(Base):
    """OTP Verification Model"""
    phone_number = Column(String(20), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    attempts = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)