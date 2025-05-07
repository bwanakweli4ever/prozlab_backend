# app/modules/auth/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Properties to receive on user creation
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        # Add your password validation logic here
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Properties to receive on user update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties to return to client
class User(UserBase):
    id: str
    
    class Config:
        orm_mode = True


# Properties for authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str