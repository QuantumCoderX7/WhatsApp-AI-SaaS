from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.dependencies import get_db_session

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """Health check endpoint to verify API and Database status."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "database": db_status,
        "service": "WhatsApp AI Automation Platform API"
    }
