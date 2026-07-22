from uuid import UUID
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text

from app.domain.conversation.models import Conversation, Message, WhatsAppAccount

class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_whatsapp_account_by_phone_number_id(self, phone_number_id: str) -> Optional[WhatsAppAccount]:
        """Find WhatsApp account details by phone number ID."""
        stmt = select(WhatsAppAccount).where(WhatsAppAccount.phone_number_id == phone_number_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_customer_phone(self, tenant_id: UUID, customer_phone: str) -> Optional[Conversation]:
        """Fetch conversation by tenant and customer phone."""
        stmt = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.customer_phone == customer_phone,
            Conversation.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, tenant_id: UUID, conversation_id: UUID) -> Optional[Conversation]:
        """Fetch conversation by ID scoped by tenant."""
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
            Conversation.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_conversation(
        self,
        tenant_id: UUID,
        whatsapp_account_id: UUID,
        customer_phone: str,
        customer_name: Optional[str] = None
    ) -> Conversation:
        """Creates a new active conversation."""
        conversation = Conversation(
            tenant_id=tenant_id,
            whatsapp_account_id=whatsapp_account_id,
            customer_phone=customer_phone,
            customer_name=customer_name,
            status="AI_ACTIVE"
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def append_message(
        self,
        tenant_id: UUID,
        conversation_id: UUID,
        sender_type: str,
        content: str,
        wamid: Optional[str] = None,
        meta_payload: Optional[dict] = None
    ) -> Message:
        """Appends a new message to conversation and updates last_activity_at timestamp."""
        message = Message(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            wamid=wamid,
            sender_type=sender_type,
            content=content,
            meta_payload=meta_payload or {}
        )
        self.session.add(message)

        # Update last activity timestamp on conversation
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(last_activity_at=datetime.now(timezone.utc))
        )
        await self.session.flush()
        return message

    async def get_recent_messages(self, conversation_id: UUID, limit: int = 10) -> List[Message]:
        """Retrieves recent N messages ordered chronologically."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        return list(reversed(messages))

    async def update_status(self, conversation_id: UUID, new_status: str) -> None:
        """Updates status of a conversation."""
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(status=new_status, updated_at=datetime.now(timezone.utc))
        )
        await self.session.flush()
        
    async def list_conversations(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Lists conversations for dashboard inbox."""
        stmt = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.deleted_at.is_(None)
        )
        if status:
            stmt = stmt.where(Conversation.status == status)
        stmt = stmt.order_by(Conversation.last_activity_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
