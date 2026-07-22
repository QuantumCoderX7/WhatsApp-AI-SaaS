from uuid import UUID
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.domain.tenant.models import User, Tenant

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides async session for API routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Decodes JWT bearer token, resolves current user, and sets tenant context in SQL session."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
        
    user_id_str: str = payload.get("sub")
    tenant_id_str: str = payload.get("tenant_id")
    
    if not user_id_str or not tenant_id_str:
        raise credentials_exception
        
    try:
        user_id = UUID(user_id_str)
        tenant_id = UUID(tenant_id_str)
    except ValueError:
        raise credentials_exception
        
    # Fetch User
    stmt = select(User).where(User.id == user_id, User.tenant_id == tenant_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise credentials_exception
        
    # Bind tenant context to PostgreSQL session for RLS policy evaluation
    await db.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'"))
    
    return user

async def get_current_tenant_id(current_user: User = Depends(get_current_user)) -> UUID:
    """Helper to extract active tenant_id from validated user."""
    return current_user.tenant_id
