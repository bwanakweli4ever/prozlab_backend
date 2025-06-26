# app/modules/auth/controllers/auth_controller.py
from typing import Any
import traceback

from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database.session import get_db
from app.modules.auth.schemas.user import User, UserCreate, Token, UserLogin
from app.modules.auth.services.auth_service import auth_service, get_current_user, get_current_superuser

# auth_service = AuthService()  # Using global instance

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
    try:
        print(f"🔍 Registration attempt for: {user_in.email}")
        print(f"🔍 User data: {user_in.model_dump()}")
        
        user = auth_service.create_user(db=db, user_in=user_in)
        
        print(f"✅ User created successfully: {user.id}")
        return user
        
    except ValueError as e:
        # Handle ValueError from our service (like "Email already registered")
        print(f"❌ Value error: {str(e)}")
        if "Email already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValidationError as e:
        # Handle Pydantic validation errors
        print(f"❌ Pydantic validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data"
        )
    except Exception as e:
        print(f"❌ Unexpected error in registration: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        user = auth_service.authenticate_user(
            db=db, email=form_data.username, password=form_data.password
        )
        access_token = auth_service.generate_token(user_id=user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )


@router.post("/login/json", response_model=Token)
def login_json(
    db: Session = Depends(get_db),
    login_data: UserLogin = Body(...),
) -> Any:
    """
    JSON login, get an access token for future requests.
    """
    try:
        user = auth_service.authenticate_user(
            db=db, email=login_data.email, password=login_data.password
        )
        access_token = auth_service.generate_token(user_id=user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"JSON login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )


@router.get("/me", response_model=User)
def read_users_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> Any:
    """
    Get the current user.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"🔍 Current user: {current_user.email}")
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