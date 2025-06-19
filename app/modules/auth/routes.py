# app/modules/auth/router.py
from fastapi import APIRouter
from app.modules.auth.controllers import auth_controller, otp_controller, email_controller

router = APIRouter()

# Authentication routes
router.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])

# OTP routes
router.include_router(otp_controller.router, prefix="/auth/otp", tags=["OTP Verification"])

# Email verification routes
router.include_router(email_controller.router, prefix="/auth/email", tags=["Email Verification"])