# app/modules/auth/services/otp_service.py
from typing import Dict, Any
from sqlalchemy.orm import Session
import random
import string
from datetime import datetime, timedelta


class OTPService:
    """Simple OTP service for development/testing"""
    
    def __init__(self):
        # In-memory storage for development (use Redis/database in production)
        self.otp_storage = {}
        
    def get_service_status(self) -> Dict[str, Any]:
        """Get OTP service status"""
        return {
            "service": "OTP Service",
            "status": "active",
            "provider": "development",
            "message": "OTP service is running in development mode"
        }
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, db: Session, phone_number: str, purpose: str = "phone_verification") -> Dict[str, Any]:
        """Send OTP to phone number (simulated for development)"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=5)
            
            # Store OTP (in production, use Redis or database)
            self.otp_storage[phone_number] = {
                "code": otp_code,
                "purpose": purpose,
                "expires_at": expires_at,
                "attempts": 0,
                "max_attempts": 3
            }
            
            # In development, just log the OTP (in production, send SMS)
            print(f"🔐 OTP for {phone_number}: {otp_code} (expires in 5 minutes)")
            
            return {
                "success": True,
                "message": f"OTP sent to {phone_number}",
                "expires_at": expires_at.isoformat(),
                "attempts_remaining": 3
            }
            
        except Exception as e:
            print(f"Error sending OTP: {str(e)}")
            return {
                "success": False,
                "message": "Failed to send OTP"
            }
    
    def verify_otp(self, db: Session, phone_number: str, otp_code: str, purpose: str = "phone_verification") -> Dict[str, Any]:
        """Verify OTP code"""
        try:
            stored_otp = self.otp_storage.get(phone_number)
            
            if not stored_otp:
                return {
                    "success": False,
                    "message": "No OTP found for this phone number"
                }
            
            # Check if OTP expired
            if datetime.utcnow() > stored_otp["expires_at"]:
                del self.otp_storage[phone_number]
                return {
                    "success": False,
                    "message": "OTP has expired"
                }
            
            # Check attempts
            if stored_otp["attempts"] >= stored_otp["max_attempts"]:
                del self.otp_storage[phone_number]
                return {
                    "success": False,
                    "message": "Maximum attempts exceeded"
                }
            
            # Verify OTP
            if stored_otp["code"] == otp_code and stored_otp["purpose"] == purpose:
                del self.otp_storage[phone_number]
                return {
                    "success": True,
                    "message": "OTP verified successfully"
                }
            else:
                # Increment attempts
                stored_otp["attempts"] += 1
                attempts_remaining = stored_otp["max_attempts"] - stored_otp["attempts"]
                
                return {
                    "success": False,
                    "message": "Invalid OTP code",
                    "attempts_remaining": attempts_remaining
                }
                
        except Exception as e:
            print(f"Error verifying OTP: {str(e)}")
            return {
                "success": False,
                "message": "Failed to verify OTP"
            }
    
    def resend_otp(self, db: Session, phone_number: str, purpose: str = "phone_verification") -> Dict[str, Any]:
        """Resend OTP"""
        # Clear existing OTP and send new one
        if phone_number in self.otp_storage:
            del self.otp_storage[phone_number]
        
        return self.send_otp(db, phone_number, purpose)
    
    def verify_and_update_profile(self, db: Session, user_id: str, phone_number: str, otp_code: str) -> Dict[str, Any]:
        """Verify OTP and update user profile"""
        # First verify OTP
        verification_result = self.verify_otp(db, phone_number, otp_code, "phone_verification")
        
        if not verification_result["success"]:
            return verification_result
        
        # TODO: Update user profile with verified phone number
        # This would typically update the user's phone number in the database
        print(f"📱 Phone number {phone_number} verified for user {user_id}")
        
        return {
            "success": True,
            "message": "Phone number verified and profile updated"
        }