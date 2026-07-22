import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, func, UniqueConstraint, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base

class WhatsAppAccount(Base):
    __tablename__ = "whatsapp_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    phone_number_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    waba_id: Mapped[str] = mapped_column(String(100), nullable=False)
    display_phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    webhook_verify_token: Mapped[str] = mapped_column(String(255), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="whatsapp_accounts")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="whatsapp_account")


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "customer_phone", name="uq_tenant_customer_phone"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    whatsapp_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("whatsapp_accounts.id"), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="AI_ACTIVE", index=True) # AI_ACTIVE, AWAITING_CUSTOMER, HUMAN_ESCALATED, CLOSED
    assigned_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    whatsapp_account: Mapped["WhatsAppAccount"] = relationship("WhatsAppAccount", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    wamid: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False) # CUSTOMER, AI, HUMAN_AGENT, SYSTEM
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_payload: Mapped[dict] = mapped_column(JSONB().with_variant(JSON, "sqlite"), server_default="{}", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
