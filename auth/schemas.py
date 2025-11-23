from uuid import UUID
from pydantic import BaseModel, EmailStr
from db.models import RolesEnum


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserOauthRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    oauth_provider: str
    oauth_id: str


class OAuthProfile(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    provider: str
    oauth_id: str


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: RolesEnum = RolesEnum.interviewer

    class Config:
        from_attributes = True
