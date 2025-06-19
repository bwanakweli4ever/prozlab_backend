from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class OTPSendRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number in international format (+1234567890)")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Ensure it starts with + and has 10-15 digits
        if not re.match(r'^\+\d{10,15}$', cleaned):
            raise ValueError('Phone number must be in international format (+1234567890)')
        
        return cleaned


class OTPVerifyRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number in international format")
    otp_code: str = Field(..., min_length=4, max_length=8, description="OTP code received via SMS")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        cleaned = re.sub(r'[^\d+]', '', v)
        if not re.match(r'^\+\d{10,15}$', cleaned):
            raise ValueError('Phone number must be in international format (+1234567890)')
        return cleaned
    
    @validator('otp_code')
    def validate_otp_code(cls, v):
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v


class OTPResponse(BaseModel):
    success: bool
    message: str
    expires_in_minutes: Optional[int] = None


class OTPVerificationResponse(BaseModel):
    success: bool
    message: str
    phone_verified: bool = False