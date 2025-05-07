"""
Database models for Proz Profile module.
File location: app/modules/proz/models/proz.py
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, Enum, Boolean, Float
from sqlalchemy.orm import relationship
import enum

from app.database.base_class import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

# app/modules/proz/models/proz.py (enhanced profile model)
class ProzProfile(Base):
    """Professional Profile Model"""
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)  # City, State format
    years_experience = Column(Integer, nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    availability = Column(String(100), nullable=True)  # e.g. "Weekdays, Evenings"
    verification_status = Column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False
    )
    is_featured = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)  # Average rating
    review_count = Column(Integer, default=0)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(100), nullable=True)
    
    # Additional professional fields
    
    education = Column(Text, nullable=True)  # Education background
    certifications = Column(Text, nullable=True)  # Professional certifications
    website = Column(String(255), nullable=True)  # Professional website
    linkedin = Column(String(255), nullable=True)  # LinkedIn profile
    preferred_contact_method = Column(String(50), nullable=True)  # Email, Phone, etc.

   
        
    # Relationships
    specialties = relationship("ProzSpecialty", back_populates="proz_profile", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="proz_profile", cascade="all, delete-orphan")

class Specialty(Base):
    """Specialty Model"""
    name = Column(String(100), nullable=False, unique=True)
    
    # Relationships
    proz_profiles = relationship("ProzSpecialty", back_populates="specialty")


class ProzSpecialty(Base):
    """Junction Table for Proz Profiles and Specialties"""
    __tablename__ = "proz_specialty"
    
    proz_id = Column(String, ForeignKey("prozprofile.id"), primary_key=True)
    specialty_id = Column(String, ForeignKey("specialty.id"), primary_key=True)
    
    # Relationships
    proz_profile = relationship("ProzProfile", back_populates="specialties")
    specialty = relationship("Specialty", back_populates="proz_profiles")


class Review(Base):
    """Review Model"""
    proz_id = Column(String, ForeignKey("prozprofile.id"), nullable=False)
    client_name = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    
    # Relationships
    proz_profile = relationship("ProzProfile", back_populates="reviews")