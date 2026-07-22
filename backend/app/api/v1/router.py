from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, webhook, conversations, knowledge, products, orders

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(webhook.router, prefix="/webhooks", tags=["WhatsApp Webhooks"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base RAG"])
api_router.include_router(products.router, prefix="/products", tags=["Catalog & Inventory"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
