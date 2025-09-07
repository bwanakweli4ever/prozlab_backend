# app/modules/auth/controllers/password_reset_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any

from app.database.session import get_db
from app.modules.auth.services.password_reset_service import PasswordResetService
from app.modules.auth.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
    ForgotPasswordResponse
)

router = APIRouter()
password_reset_service = PasswordResetService()


@router.post("/forgot", response_model=ForgotPasswordResponse)
def forgot_password(
    *,
    db: Session = Depends(get_db),
    request: ForgotPasswordRequest,
) -> Any:
    """
    Request a password reset email.
    
    This endpoint will send a password reset email to the provided email address.
    For security reasons, it will always return success even if the email doesn't exist.
    """
    try:
        result = password_reset_service.send_reset_email(db, request.email)
        
        if result["success"]:
            return ForgotPasswordResponse(
                success=True,
                message=result["message"],
                development_mode=result.get("development_mode"),
                token=result.get("token")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in forgot password endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        )


@router.post("/reset", response_model=PasswordResetResponse)
def reset_password(
    *,
    db: Session = Depends(get_db),
    request: ResetPasswordRequest,
) -> Any:
    """
    Reset password using a valid reset token.
    
    This endpoint allows users to set a new password using a valid reset token
    that was sent to their email address.
    """
    try:
        result = password_reset_service.reset_password(
            db, 
            request.token, 
            request.new_password
        )
        
        if result["success"]:
            return PasswordResetResponse(
                success=True,
                message=result["message"]
            )
        else:
            error_code = result.get("error_code", "RESET_FAILED")
            status_code = status.HTTP_400_BAD_REQUEST
            
            # Set appropriate status codes for different error types
            if error_code == "INVALID_TOKEN":
                status_code = status.HTTP_404_NOT_FOUND
            elif error_code == "TOKEN_EXPIRED":
                status_code = status.HTTP_410_GONE
            elif error_code == "TOKEN_USED":
                status_code = status.HTTP_410_GONE
            elif error_code == "USER_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            elif error_code == "ACCOUNT_INACTIVE":
                status_code = status.HTTP_403_FORBIDDEN
            
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in reset password endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        )


@router.get("/validate", response_model=PasswordResetResponse)
def validate_reset_token(
    *,
    db: Session = Depends(get_db),
    token: str = Query(..., description="Password reset token to validate"),
) -> Any:
    """
    Validate a password reset token.
    
    This endpoint checks if a password reset token is valid and not expired.
    Useful for frontend applications to check token validity before showing
    the reset password form.
    """
    try:
        result = password_reset_service.validate_reset_token(db, token)
        
        if result["success"]:
            return PasswordResetResponse(
                success=True,
                message=result["message"]
            )
        else:
            error_code = result.get("error_code", "VALIDATION_FAILED")
            status_code = status.HTTP_400_BAD_REQUEST
            
            # Set appropriate status codes for different error types
            if error_code == "INVALID_TOKEN":
                status_code = status.HTTP_404_NOT_FOUND
            elif error_code == "TOKEN_EXPIRED":
                status_code = status.HTTP_410_GONE
            elif error_code == "TOKEN_USED":
                status_code = status.HTTP_410_GONE
            elif error_code == "USER_NOT_FOUND":
                status_code = status.HTTP_404_NOT_FOUND
            
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in validate token endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        )
