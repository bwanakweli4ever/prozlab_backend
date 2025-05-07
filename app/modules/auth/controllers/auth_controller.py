# app/modules/auth/controllers/auth_controller.py
from typing import Any

from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.auth.schemas.user import User, UserCreate, Token, UserLogin
from app.modules.auth.services.auth_service import AuthService

auth_service = AuthService()

router = APIRouter()


@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    user = auth_service.create_user(db=db, user_in=user_in)
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = auth_service.authenticate_user(
        db=db, email=form_data.username, password=form_data.password
    )
    access_token = auth_service.generate_token(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
def login_json(
    db: Session = Depends(get_db),
    login_data: UserLogin = Body(...),
) -> Any:
    """
    JSON login, get an access token for future requests.
    """
    user = auth_service.authenticate_user(
        db=db, email=login_data.email, password=login_data.password
    )
    access_token = auth_service.generate_token(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/users", response_model=list[User])
def get_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_superuser),
) -> Any:
    """
    Get all users. Only accessible to superusers.
    """
    users = auth_service.user_repository.get_all(db=db, skip=skip, limit=limit)
    return users