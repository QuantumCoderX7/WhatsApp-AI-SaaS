import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base

# Import all models to register mappers on Base.metadata
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount, Conversation, Message
from app.domain.inventory.models import Product, InventoryItem, InventoryReservation
from app.domain.order.models import Order, OrderItem
from app.domain.rag.models import KnowledgeDocument, KnowledgeChunk
from app.core.security import get_password_hash

async def seed_demo_user():
    # Ensure database tables are created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if admin user already exists
        stmt = select(User).where(User.email == "admin@demo.com")
        res = await session.execute(stmt)
        if res.scalar_one_or_none():
            print("Default admin user already exists.")
            return

        tenant = Tenant(
            name="Demo Store",
            slug="demo-store",
            plan_tier="starter"
        )
        session.add(tenant)
        await session.flush()

        user = User(
            tenant_id=tenant.id,
            email="admin@demo.com",
            password_hash=get_password_hash("admin123456"),
            full_name="Demo Admin",
            role="admin"
        )
        session.add(user)
        await session.commit()
        print("Successfully created seed admin account.")

if __name__ == "__main__":
    asyncio.run(seed_demo_user())
