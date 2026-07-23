import asyncio
from sqlalchemy import select, update, delete
from app.core.database import AsyncSessionLocal
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount, Conversation, Message

async def consolidate():
    async with AsyncSessionLocal() as session:
        # Get first user rayyanasim19@gmail.com
        stmt = select(User).where(User.email == "rayyanasim19@gmail.com").order_by(User.created_at.asc())
        users = (await session.execute(stmt)).scalars().all()

        if not users:
            print("No user found for rayyanasim19@gmail.com")
            return

        primary_user = users[0]
        target_tenant_id = primary_user.tenant_id
        print(f"Primary User ID: {primary_user.id} | Target Tenant ID: {target_tenant_id}")

        # Delete duplicate user rows for rayyanasim19@gmail.com if any
        if len(users) > 1:
            for dup_user in users[1:]:
                await session.delete(dup_user)
            await session.flush()

        # Update all WhatsApp Accounts to target_tenant_id
        await session.execute(
            update(WhatsAppAccount).values(tenant_id=target_tenant_id)
        )

        # Update all Conversations to target_tenant_id
        await session.execute(
            update(Conversation).values(tenant_id=target_tenant_id)
        )

        # Update all Messages to target_tenant_id
        await session.execute(
            update(Message).values(tenant_id=target_tenant_id)
        )

        await session.commit()
        print("CONSOLIDATION SUCCESSFUL! All conversations and WhatsApp accounts are now linked to primary user's tenant.")

if __name__ == "__main__":
    asyncio.run(consolidate())
