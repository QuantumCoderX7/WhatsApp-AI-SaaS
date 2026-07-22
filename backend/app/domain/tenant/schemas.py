from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100)

class TenantOut(BaseModel):
    id: UUID
    name: str
    slug: str
    plan_tier: str
    is_active: bool
    monthly_message_limit: int
    monthly_messages_used: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserRegisterRequest(BaseModel):
    tenant_name: str = Field(..., min_length=2, max_length=255)
    tenant_slug: str = Field(..., min_length=2, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
    tenant_id: UUID
    role: str

class UserProfileOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    tenant: TenantOut

    class Config:
        from_attributes = True
