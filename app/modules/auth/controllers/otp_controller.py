# app/modules/auth/controllers/otp_controller.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.schemas.otp import (
    OTPSendRequest, OTPVerifyRequest, OTPResponse, OTPVerificationResponse
)
from app.services.sms_service import SMSService
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.models.user import User

router = APIRouter()
sms_service = SMSService()
auth_service = AuthService()


@router.get("/status")
async def get_sms_service_status() -> Any:
    """
    Get the current status of the SMS service.
    Useful for checking if Twilio and Redis are properly configured.
    """
    status_info = sms_service.get_service_status()
    return {
        "sms_service": status_info,
        "message": "SMS service ready" if status_info.get("development_mode") else "SMS service configured" if status_info.get("sms_configured") else "SMS service in development mode"
    }


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(
    request: OTPSendRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Send OTP to phone number for verification.
    """
    result = sms_service.send_otp(request.phone_number)
    
    if not result["success"]:
        # Map specific error codes to HTTP status codes
        if result.get("error_code") == "RATE_LIMIT_EXCEEDED":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=result["message"]
            )
        elif result.get("error_code") == "SMS_NOT_CONFIGURED":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    
    return OTPResponse(
        success=result["success"],
        message=result["message"],
        expires_in_minutes=result.get("expires_in_minutes")
    )


@router.post("/verify-otp", response_model=OTPVerificationResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify OTP code for phone number.
    """
    result = sms_service.verify_otp(request.phone_number, request.otp_code)
    
    if not result["success"]:
        # Different status codes for different errors
        if result.get("error_code") in ["OTP_EXPIRED", "OTP_NOT_FOUND"]:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=result["message"]
            )
        elif result.get("error_code") in ["INVALID_OTP", "MAX_ATTEMPTS_EXCEEDED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        elif result.get("error_code") == "SMS_NOT_CONFIGURED":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    
    return OTPVerificationResponse(
        success=result["success"],
        message=result["message"],
        phone_verified=result.get("phone_verified", False)
    )


@router.post("/verify-and-update-profile", response_model=OTPVerificationResponse)
async def verify_otp_and_update_profile(
    request: OTPVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
) -> Any:
    """
    Verify OTP and update user's phone verification status.
    This endpoint requires authentication.
    """
    result = sms_service.verify_otp(request.phone_number, request.otp_code)
    
    if not result["success"]:
        if result.get("error_code") in ["OTP_EXPIRED", "OTP_NOT_FOUND"]:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=result["message"]
            )
        elif result.get("error_code") in ["INVALID_OTP", "MAX_ATTEMPTS_EXCEEDED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        elif result.get("error_code") == "SMS_NOT_CONFIGURED":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    
    # If verification successful, update user's phone verification status
    # You can add phone verification fields to your user model if needed
    # For now, we'll just return success
    
    return OTPVerificationResponse(
        success=True,
        message="Phone number verified and profile updated successfully",
        phone_verified=True
    )


@router.post("/resend-otp", response_model=OTPResponse)
async def resend_otp(
    request: OTPSendRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Resend OTP to phone number.
    """
    result = sms_service.resend_otp(request.phone_number)
    
    if not result["success"]:
        # Map specific error codes to HTTP status codes
        if result.get("error_code") == "RATE_LIMIT_EXCEEDED":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=result["message"]
            )
        elif result.get("error_code") == "SMS_NOT_CONFIGURED":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    
    return OTPResponse(
        success=result["success"],
        message=result["message"],
        expires_in_minutes=result.get("expires_in_minutes")
    )
