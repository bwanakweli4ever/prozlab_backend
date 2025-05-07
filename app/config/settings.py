# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Modular App"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fastapi_modular"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()