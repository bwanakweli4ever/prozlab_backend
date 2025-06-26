# app/modules/auth/repositories/user_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
import traceback

from app.modules.auth.models.user import User
from app.core.security import get_password_hash, verify_password


class UserRepository:
    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            print(f"🔍 Looking for user with ID: {user_id}")
            
            # Convert string to UUID if necessary
            if isinstance(user_id, str):
                user_uuid = uuid.UUID(user_id)
            else:
                user_uuid = user_id
                
            user = db.query(User).filter(User.id == user_uuid).first()
            print(f"🔍 Found user: {user}")
            return user
        except ValueError as e:
            print(f"❌ Invalid UUID string: {user_id}, error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error in get_by_id: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            print(f"🔍 Looking for user with email: {email}")
            user = db.query(User).filter(User.email == email).first()
            print(f"🔍 Found user: {user}")
            return user
        except Exception as e:
            print(f"❌ Error in get_by_email: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users"""
        try:
            users = db.query(User).offset(skip).limit(limit).all()
            print(f"🔍 Found {len(users)} users")
            return users
        except Exception as e:
            print(f"❌ Error in get_all: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return []

    def create(self, db: Session, obj_in: dict) -> User:
        """Create a new user"""
        try:
            print(f"🔍 Creating user with data: {obj_in}")
            
            # Create the user object
            db_obj = User(
                email=obj_in["email"],
                hashed_password=get_password_hash(obj_in["password"]),
                first_name=obj_in.get("first_name"),
                last_name=obj_in.get("last_name"),
                is_superuser=obj_in.get("is_superuser", False),
                is_active=obj_in.get("is_active", True),
                is_verified=obj_in.get("is_verified", False),
            )
            
            print(f"🔍 User object created: {db_obj}")
            print(f"🔍 User object type: {type(db_obj)}")
            print(f"🔍 User object __dict__: {db_obj.__dict__}")
            
            # Add to session
            db.add(db_obj)
            print("🔍 User added to session")
            
            # Commit
            db.commit()
            print("🔍 Transaction committed")
            
            # Refresh
            db.refresh(db_obj)
            print(f"🔍 User refreshed: {db_obj}")
            print(f"🔍 User ID after refresh: {db_obj.id}")
            
            return db_obj
            
        except IntegrityError as e:
            db.rollback()
            print(f"❌ Database integrity error: {str(e)}")
            raise ValueError("Email already exists")
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating user: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise

    def update(self, db: Session, db_obj: User, obj_in: dict) -> User:
        """Update an existing user"""
        try:
            update_data = obj_in.copy()
            
            if "password" in update_data:
                hashed_password = get_password_hash(update_data["password"])
                del update_data["password"]
                update_data["hashed_password"] = hashed_password
                
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
                    
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            print(f"❌ Error updating user: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise

    def delete(self, db: Session, user_id: str) -> bool:
        """Delete a user"""
        try:
            user = self.get_by_id(db, user_id)
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Error deleting user: {str(e)}")
            return False
        
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        try:
            user = self.get_by_email(db=db, email=email)
            if not user:
                print("❌ User not found")
                return None
            if not verify_password(password, user.hashed_password):
                print("❌ Password verification failed")
                return None
            print("✅ User authenticated successfully")
            return user
        except Exception as e:
            print(f"❌ Error in authenticate: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            return None