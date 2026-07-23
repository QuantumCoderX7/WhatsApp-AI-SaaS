from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, get_current_user, get_current_tenant_id
from app.core.config import settings
from app.domain.tenant.models import User
from app.domain.conversation.models import WhatsAppAccount
from app.domain.conversation.repository import ConversationRepository
from app.domain.conversation.schemas import (
    ConversationOut,
    MessageOut,
    HandoffToggleRequest,
    SendMessageRequest
)
from app.domain.conversation.state_machine import ConversationStateMachine, ConversationState
from app.domain.conversation.outbound import WhatsAppOutboundService

router = APIRouter()

@router.get("", response_model=List[ConversationOut])
async def list_tenant_conversations(
    status: Optional[str] = Query(None, description="Filter by status: AI_ACTIVE, HUMAN_ESCALATED, CLOSED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists conversations for the active tenant business."""
    repo = ConversationRepository(db)
    return await repo.list_conversations(tenant_id, status=status, skip=skip, limit=limit)

@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation_by_id(
    conversation_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves conversation metadata by ID."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(tenant_id, conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conv

@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves chat message history for a conversation."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(tenant_id, conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    return await repo.get_recent_messages(conversation_id, limit=limit)

@router.post("/{conversation_id}/send-message", response_model=MessageOut)
async def send_human_agent_message(
    conversation_id: UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Dispatches a human agent response to the customer via Meta WhatsApp Cloud API."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(current_user.tenant_id, conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Append human agent message to database
    message = await repo.append_message(
        tenant_id=current_user.tenant_id,
        conversation_id=conversation_id,
        sender_type="HUMAN",
        content=payload.content
    )

    await db.commit()

    # Dispatch outbound message via Meta WhatsApp API
    stmt = select(WhatsAppAccount).where(WhatsAppAccount.id == conv.whatsapp_account_id)
    wa_res = await db.execute(stmt)
    wa_account = wa_res.scalar_one_or_none()

    phone_id = wa_account.phone_number_id if wa_account else settings.META_PHONE_NUMBER_ID
    token = (wa_account.access_token_encrypted if wa_account else None) or settings.META_ACCESS_TOKEN

    await WhatsAppOutboundService.send_text_message(
        phone_number_id=phone_id,
        access_token=token,
        recipient_phone=conv.customer_phone,
        text_body=payload.content
    )

    return message

@router.post("/{conversation_id}/handoff", response_model=ConversationOut)
async def toggle_human_handoff(
    conversation_id: UUID,
    payload: HandoffToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Toggles human takeover mode on or resumes AI automation."""
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(current_user.tenant_id, conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    target_state = ConversationState.HUMAN_ESCALATED if payload.action == "takeover" else ConversationState.AI_ACTIVE
    new_status = ConversationStateMachine.transition(conv.status, target_state)
    
    await repo.update_status(conversation_id, new_status)

    # Log system event message
    event_text = (
        f"[System] Human Agent {current_user.full_name} took over conversation."
        if payload.action == "takeover"
        else f"[System] Human Agent {current_user.full_name} re-enabled AI automation."
    )
    await repo.append_message(
        tenant_id=current_user.tenant_id,
        conversation_id=conversation_id,
        sender_type="SYSTEM",
        content=event_text
    )
    await db.commit()
    await db.refresh(conv)

    return conv
