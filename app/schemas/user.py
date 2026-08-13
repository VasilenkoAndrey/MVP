from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.trophy import TrophyStatus
from enum import Enum


class RoleEnum(str, Enum):
    USER = "USER"
    MEASURER = "MEASURER"
    EXPERT = "EXPERT"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    role: RoleEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int
    role: str
    exp: datetime
