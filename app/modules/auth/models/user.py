# app/modules/auth/models/user.py
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class User(Base):
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)