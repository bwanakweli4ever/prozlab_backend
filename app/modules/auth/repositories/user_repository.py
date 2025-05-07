# app/modules/auth/repositories/user_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.modules.auth.models.user import User
from app.core.security import get_password_hash, verify_password


class UserRepository:
    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> User:
        db_obj = User(
            email=obj_in["email"],
            hashed_password=get_password_hash(obj_in["password"]),
            first_name=obj_in.get("first_name"),
            last_name=obj_in.get("last_name"),
            is_superuser=obj_in.get("is_superuser", False),
            is_active=obj_in.get("is_active", True),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: dict) -> User:
        update_data = obj_in.copy()
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
        
    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db=db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user