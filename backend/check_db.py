import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount, Conversation, Message

async def check():
    async with AsyncSessionLocal() as session:
        tenants = (await session.execute(select(Tenant))).scalars().all()
        print("=== TENANTS ===")
        for t in tenants:
            print(f"Tenant ID: {t.id} | Name: {t.name} | Slug: {t.slug}")

        users = (await session.execute(select(User))).scalars().all()
        print("\n=== USERS ===")
        for u in users:
            print(f"User ID: {u.id} | Email: {u.email} | Tenant ID: {u.tenant_id}")

        accounts = (await session.execute(select(WhatsAppAccount))).scalars().all()
        print("\n=== WHATSAPP ACCOUNTS ===")
        for a in accounts:
            print(f"Account ID: {a.id} | Phone ID: {a.phone_number_id} | Tenant ID: {a.tenant_id}")

        convs = (await session.execute(select(Conversation))).scalars().all()
        print("\n=== CONVERSATIONS ===")
        for c in convs:
            print(f"Conv ID: {c.id} | Phone: {c.customer_phone} | Name: {c.customer_name} | Tenant ID: {c.tenant_id}")

        msgs = (await session.execute(select(Message))).scalars().all()
        print(f"\nTotal Messages in DB: {len(msgs)}")

if __name__ == "__main__":
    asyncio.run(check())
