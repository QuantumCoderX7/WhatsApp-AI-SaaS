import asyncio
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount, Conversation, Message

async def link_all_to_user_tenant():
    async with AsyncSessionLocal() as session:
        # Find user rayyanasim19@gmail.com
        stmt = select(User).where(User.email == "rayyanasim19@gmail.com").order_by(User.created_at.desc())
        user = (await session.execute(stmt)).scalars().first()

        if not user:
            print("User rayyanasim19@gmail.com not found!")
            return

        target_tenant_id = user.tenant_id
        print(f"Linking all WhatsApp accounts, conversations, and messages to Tenant ID: {target_tenant_id}")

        # Update WhatsApp Accounts
        await session.execute(
            update(WhatsAppAccount).values(tenant_id=target_tenant_id)
        )

        # Update Conversations
        await session.execute(
            update(Conversation).values(tenant_id=target_tenant_id)
        )

        # Update Messages
        await session.execute(
            update(Message).values(tenant_id=target_tenant_id)
        )

        await session.commit()
        print("SUCCESS! All database conversations are now linked to rayyanasim19@gmail.com's tenant.")

if __name__ == "__main__":
    asyncio.run(link_all_to_user_tenant())
