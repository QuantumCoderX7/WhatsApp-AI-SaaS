from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router

# Import all models to register on Base.metadata
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount, Conversation, Message
from app.domain.inventory.models import Product, InventoryItem, InventoryReservation
from app.domain.order.models import Order, OrderItem
from app.domain.rag.models import KnowledgeDocument, KnowledgeChunk

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (For zero-config local dev & SQLite)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"Started {settings.PROJECT_NAME} API server in {settings.ENVIRONMENT} mode.")
    yield
    print("Shutting down gateway...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
