from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.api.dependencies import get_db_session, get_current_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.domain.tenant.models import Tenant, User
from app.domain.tenant.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileOut
)

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant_and_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Registers a new tenant business and admin user account."""
    # 1. Check if slug exists
    slug_check = await db.execute(select(Tenant).where(Tenant.slug == payload.tenant_slug))
    if slug_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug is already taken. Please choose a unique business identifier."
        )

    # 2. Create Tenant
    tenant = Tenant(
        name=payload.tenant_name,
        slug=payload.tenant_slug,
        plan_tier="starter"
    )
    db.add(tenant)
    await db.flush()

    # 3. Create Admin User
    user = User(
        tenant_id=tenant.id,
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        role="admin"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 4. Generate Access Token
    access_token = create_access_token(
        subject=user.id,
        tenant_id=tenant.id,
        role=user.role
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticates user and returns JWT token."""
    # Find user by email
    stmt = select(User).where(User.email == payload.email.lower(), User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        subject=user.id,
        tenant_id=user.tenant_id,
        role=user.role
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role
    )

@router.get("/me", response_model=UserProfileOut)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Returns profile for currently authenticated user."""
    stmt = select(User).where(User.id == current_user.id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user
