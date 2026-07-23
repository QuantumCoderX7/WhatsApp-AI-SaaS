import asyncio
from app.core.database import AsyncSessionLocal
from app.domain.tenant.schemas import UserRegisterRequest
from app.api.v1.endpoints.auth import register_tenant_and_user

# Import all models to ensure mappers are registered
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount, Conversation, Message
from app.domain.inventory.models import Product, InventoryItem, InventoryReservation
from app.domain.order.models import Order, OrderItem
from app.domain.rag.models import KnowledgeDocument, KnowledgeChunk

async def main():
    async with AsyncSessionLocal() as session:
        payload = UserRegisterRequest(
            tenant_name="Rayyan",
            tenant_slug="rayyan-store",
            full_name="rayyanasim",
            email="rayyanasim19@gmail.com",
            password="password123"
        )
        try:
            res = await register_tenant_and_user(payload, session)
            print("SUCCESS:", res)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
