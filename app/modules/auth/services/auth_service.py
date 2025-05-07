# app/modules/auth/services/auth_service.py
from datetime import timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.exceptions import AuthenticationException, NotFoundException
from app.core.security import create_access_token
from app.database.session import get_db
from app.modules.auth.models.user import User
from app.modules.auth.repositories.user_repository import UserRepository
from app.modules.auth.schemas.user import TokenPayload, UserCreate, UserUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

user_repository = UserRepository()


class AuthService:
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        # Check if user with same email exists
        user = user_repository.get_by_email(db, email=user_in.email)
        if user:
            raise ValidationError("Email already registered")
        
        # Create new user
        user_in_data = user_in.dict()
        return user_repository.create(db=db, obj_in=user_in_data)

    def update_user(self, db: Session, user_id: str, user_in: UserUpdate) -> User:
        user = user_repository.get_by_id(db, user_id=user_id)
        if not user:
            raise NotFoundException("User not found")
        
        user_in_data = user_in.dict(exclude_unset=True)
        return user_repository.update(db=db, db_obj=user, obj_in=user_in_data)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        user = user_repository.authenticate(db=db, email=email, password=password)
        if not user:
            raise AuthenticationException("Incorrect email or password")
        if not user.is_active:
            raise AuthenticationException("Inactive user account")
        return user

    def generate_token(self, user_id: str) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )

    def get_current_user(
        self, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
    ) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise AuthenticationException()
            
        user = user_repository.get_by_id(db, user_id=token_data.sub)
        if not user:
            raise AuthenticationException()
        if not user.is_active:
            raise AuthenticationException("Inactive user")
        return user

    def get_current_superuser(
        self, current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.is_superuser:
            raise AuthenticationException("Not enough permissions")
        return current_user