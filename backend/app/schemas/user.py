from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    family_id: int | None
    family_role: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FamilyCreate(BaseModel):
    name: str


class FamilyResponse(BaseModel):
    id: int
    name: str
    members: list[UserResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class FamilyInvite(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str
