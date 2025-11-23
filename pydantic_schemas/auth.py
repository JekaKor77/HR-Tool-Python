from enum import Enum

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

from db.models import RolesEnum


class UserBase(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=120)


class UserOauthRegister(UserBase):
    oauth_provider: str
    oauth_id: str


class UserRead(UserBase):
    id: UUID
    role: RolesEnum = RolesEnum.interviewer

    class Config:
        from_attributes = True
