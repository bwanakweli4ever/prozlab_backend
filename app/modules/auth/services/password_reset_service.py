# app/modules/auth/services/password_reset_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import logging

from app.modules.auth.models.user import User
from app.modules.auth.models.password_reset import PasswordResetToken
from app.modules.auth.repositories.user_repository import UserRepository
from app.modules.auth.repositories.password_reset_repository import PasswordResetRepository
from app.core.security import get_password_hash, verify_password
from app.services.email_service import EmailService
from app.core.exceptions import NotFoundException, AuthenticationException

logger = logging.getLogger(__name__)


class PasswordResetService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.password_reset_repository = PasswordResetRepository()
        self.email_service = EmailService()
    
    def _create_reset_email(self, email: str, token: str, user_name: str = None) -> tuple:
        """Create password reset email content"""
        # Create reset URL
        reset_url = f"http://localhost:8000/api/v1/auth/password/reset?token={token}"
        
        # Email subject
        subject = "Reset Your Password"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #dc3545;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #dc3545;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>Hello{' ' + user_name if user_name else ''},</p>
                <p>We received a request to reset your password. Click the button below to reset it:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #fff; padding: 10px; border-radius: 3px;">
                    {reset_url}
                </p>
                
                <div class="warning">
                    <strong>Important:</strong>
                    <ul>
                        <li>This link will expire in 1 hour</li>
                        <li>If you didn't request this password reset, please ignore this email</li>
                        <li>Your password will remain unchanged until you create a new one</li>
                    </ul>
                </div>
                
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>This email was sent from your account security system</p>
                <p>Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Password Reset Request
        
        Hello{' ' + user_name if user_name else ''},
        
        We received a request to reset your password. Please visit this link to reset it:
        {reset_url}
        
        Important:
        - This link will expire in 1 hour
        - If you didn't request this password reset, please ignore this email
        - Your password will remain unchanged until you create a new one
        
        If you didn't request a password reset, you can safely ignore this email.
        
        Best regards,
        Your Account Security Team
        """
        
        return subject, html_body, text_body
    
    def send_reset_email(self, db: Session, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            # Check if user exists
            user = self.user_repository.get_by_email(db, email)
            if not user:
                # Don't reveal if email exists or not for security
                return {
                    "success": True,
                    "message": "If an account with that email exists, a password reset link has been sent.",
                    "development_mode": self.email_service.development_mode
                }
            
            # Check if user is active
            if not user.is_active:
                return {
                    "success": False,
                    "message": "Account is inactive. Please contact support.",
                    "error_code": "ACCOUNT_INACTIVE"
                }
            
            # Create password reset token
            token_obj = self.password_reset_repository.create(
                db=db, 
                user_id=str(user.id), 
                expires_in_hours=1
            )
            
            if not token_obj:
                return {
                    "success": False,
                    "message": "Failed to create reset token. Please try again.",
                    "error_code": "TOKEN_CREATION_FAILED"
                }
            
            # Create email content
            user_name = f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else None
            subject, html_body, text_body = self._create_reset_email(email, token_obj.token, user_name)
            
            if self.email_service.development_mode:
                # Development mode - log reset link
                reset_url = f"http://localhost:8000/api/v1/auth/password/reset?token={token_obj.token}"
                logger.info(f"📧 DEVELOPMENT MODE - Password reset for {email}")
                logger.info(f"🔗 Reset URL: {reset_url}")
                print(f"📧 DEVELOPMENT MODE - Password reset for {email}")
                print(f"🔗 Reset URL: {reset_url}")
                
                message = "Password reset email sent (development mode). Check console for reset link."
                
            else:
                # Production mode - send actual email
                self.email_service._send_smtp_email(email, subject, html_body, text_body)
                message = "Password reset email sent successfully"
            
            return {
                "success": True,
                "message": message,
                "development_mode": self.email_service.development_mode,
                "token": token_obj.token if self.email_service.development_mode else None
            }
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {email}: {str(e)}")
            return {
                "success": False,
                "message": "Failed to send password reset email",
                "error_code": "EMAIL_SEND_FAILED",
                "error_details": str(e)
            }
    
    def reset_password(self, db: Session, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using token"""
        try:
            # Get token from database
            token_obj = self.password_reset_repository.get_by_token(db, token)
            if not token_obj:
                return {
                    "success": False,
                    "message": "Invalid or expired reset token",
                    "error_code": "INVALID_TOKEN"
                }
            
            # Check if token is valid
            if not token_obj.is_valid:
                if token_obj.is_used:
                    return {
                        "success": False,
                        "message": "Reset token has already been used",
                        "error_code": "TOKEN_USED"
                    }
                elif token_obj.is_expired:
                    return {
                        "success": False,
                        "message": "Reset token has expired",
                        "error_code": "TOKEN_EXPIRED"
                    }
            
            # Get user
            user = self.user_repository.get_by_id(db, str(token_obj.user_id))
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND"
                }
            
            # Check if user is active
            if not user.is_active:
                return {
                    "success": False,
                    "message": "Account is inactive",
                    "error_code": "ACCOUNT_INACTIVE"
                }
            
            # Hash new password
            hashed_password = get_password_hash(new_password)
            
            # Update user password
            user.hashed_password = hashed_password
            db.commit()
            
            # Mark token as used
            self.password_reset_repository.mark_as_used(db, token)
            
            # Clean up expired tokens for this user
            self.password_reset_repository.delete_expired_tokens(db)
            
            logger.info(f"✅ Password reset successful for user: {user.email}")
            
            return {
                "success": True,
                "message": "Password reset successfully",
                "user_id": str(user.id),
                "email": user.email
            }
            
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "message": "Failed to reset password",
                "error_code": "RESET_FAILED",
                "error_details": str(e)
            }
    
    def validate_reset_token(self, db: Session, token: str) -> Dict[str, Any]:
        """Validate a password reset token"""
        try:
            token_obj = self.password_reset_repository.get_by_token(db, token)
            if not token_obj:
                return {
                    "success": False,
                    "message": "Invalid reset token",
                    "error_code": "INVALID_TOKEN"
                }
            
            if not token_obj.is_valid:
                if token_obj.is_used:
                    return {
                        "success": False,
                        "message": "Reset token has already been used",
                        "error_code": "TOKEN_USED"
                    }
                elif token_obj.is_expired:
                    return {
                        "success": False,
                        "message": "Reset token has expired",
                        "error_code": "TOKEN_EXPIRED"
                    }
            
            # Get user info
            user = self.user_repository.get_by_id(db, str(token_obj.user_id))
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "error_code": "USER_NOT_FOUND"
                }
            
            return {
                "success": True,
                "message": "Token is valid",
                "user_id": str(user.id),
                "email": user.email,
                "expires_at": token_obj.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating reset token: {str(e)}")
            return {
                "success": False,
                "message": "Failed to validate token",
                "error_code": "VALIDATION_FAILED",
                "error_details": str(e)
            }
