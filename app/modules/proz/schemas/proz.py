"""
Schemas for Proz Profile module.
File location: app/modules/proz/schemas/proz.py
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import enum


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# app/modules/proz/schemas/proz.py (enhanced schemas)
class ProzProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    preferred_contact_method: Optional[str] = None


class ProzProfileCreate(ProzProfileBase):
    pass


class ProzProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    preferred_contact_method: Optional[str] = None


class ProzProfileResponse(ProzProfileBase):
    id: str
    verification_status: VerificationStatus
    is_featured: bool
    rating: float
    review_count: int
    email_verified: bool
    created_at: datetime
    
    class Config:
        orm_mode = True