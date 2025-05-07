"""
Service layer for Proz Profile module.
File location: app/modules/proz/services/proz_service.py
"""

from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException, status
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.modules.proz.repositories.proz_repository import (
    ProzProfileRepository, SpecialtyRepository, ReviewRepository
)
from app.modules.proz.models.proz import ProzProfile, Specialty, ProzSpecialty, Review, VerificationStatus
from app.modules.proz.schemas.proz import (
    ProzProfileCreate, ProzProfileUpdate, VerificationUpdate, 
    ProzProfileResponse, ProzProfileDetailResponse, PaginatedProzProfiles
)
from app.config.settings import settings


class ProzService:
    """
    Service class for Proz Profile operations
    Handles business logic between controllers and repositories
    """
    
    def __init__(self):
        self.profile_repo = ProzProfileRepository()
        self.specialty_repo = SpecialtyRepository()
        self.review_repo = ReviewRepository()
    
    def get_profile_by_email(self, db: Session, email: str) -> Optional[ProzProfile]:
        """Get a profile by email address"""
        profile = self.profile_repo.get_by_email(db=db, email=email)
        return profile
    
    def get_all_profiles(
        self, 
        db: Session, 
        page: int = 1, 
        limit: int = 10,
        location: Optional[str] = None,
        specialty: Optional[str] = None,
        min_experience: Optional[int] = None,
        max_rate: Optional[float] = None,
        availability: Optional[str] = None,
    ) -> PaginatedProzProfiles:
        """Get all verified profiles with optional filtering and pagination"""
        skip = (page - 1) * limit
        
        profiles, total = self.profile_repo.get_all(
            db=db,
            skip=skip,
            limit=limit,
            location=location,
            specialty=specialty,
            min_experience=min_experience,
            max_rate=max_rate,
            availability=availability,
            verification_status=VerificationStatus.VERIFIED
        )
        
        return PaginatedProzProfiles(
            professionals=[ProzProfileResponse.from_orm(p) for p in profiles],
            total=total,
            page=page,
            limit=limit
        )
    
    def get_featured_profiles(self, db: Session, limit: int = 10) -> List[ProzProfileResponse]:
        """Get featured verified profiles"""
        profiles = self.profile_repo.get_featured(db=db, limit=limit)
        return [ProzProfileResponse.from_orm(p) for p in profiles]
    
    def get_profile_by_id(self, db: Session, profile_id: str) -> ProzProfileDetailResponse:
        """Get a profile by ID with detailed information including reviews"""
        profile = self.profile_repo.get_by_id(db=db, profile_id=profile_id)
        if not profile or profile.verification_status != VerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )
        
        return ProzProfileDetailResponse.from_orm(profile)
    
    def create_profile(self, db: Session, profile_data: ProzProfileCreate) -> ProzProfileResponse:
        """Create a new professional profile with specialties"""
        # Check for existing profile with same email
        existing_profile = self.profile_repo.get_by_email(db=db, email=profile_data.email)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A profile with this email already exists"
            )
        
        # Process specialties
        specialties = []
        for specialty_id in profile_data.specialties:
            specialty = self.specialty_repo.get_by_id(db=db, specialty_id=specialty_id)
            if not specialty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Specialty with ID {specialty_id} not found"
                )
            specialties.append(specialty)
        
        # Create profile
        profile_dict = profile_data.dict(exclude={"specialties"})
        profile = self.profile_repo.create(db=db, profile_data=profile_dict, specialties=specialties)
        
        return ProzProfileResponse.from_orm(profile)
    
    def update_profile(
        self, 
        db: Session, 
        profile_id: str, 
        profile_data: ProzProfileUpdate
    ) -> ProzProfileResponse:
        """Update an existing professional profile and its specialties"""
        # Check if profile exists
        profile = self.profile_repo.get_by_id(db=db, profile_id=profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )
        
        # Check if email is being changed and already exists
        if profile_data.email and profile_data.email != profile.email:
            existing_profile = self.profile_repo.get_by_email(db=db, email=profile_data.email)
            if existing_profile and existing_profile.id != profile_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A profile with this email already exists"
                )
        
        # Process specialties if provided
        specialties = None
        if profile_data.specialties is not None:
            specialties = []
            for specialty_id in profile_data.specialties:
                specialty = self.specialty_repo.get_by_id(db=db, specialty_id=specialty_id)
                if not specialty:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Specialty with ID {specialty_id} not found"
                    )
                specialties.append(specialty)
        
        # Update profile
        profile_dict = profile_data.dict(exclude={"specialties"}, exclude_unset=True)
        updated_profile = self.profile_repo.update(db=db, profile=profile, update_data=profile_dict, specialties=specialties)
        
        return ProzProfileResponse.from_orm(updated_profile)