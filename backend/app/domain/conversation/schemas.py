from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

# =============================================================================
# META WHATSAPP WEBHOOK PAYLOAD SCHEMAS
# =============================================================================

class WhatsAppProfile(BaseModel):
    name: Optional[str] = None

class WhatsAppContact(BaseModel):
    profile: Optional[WhatsAppProfile] = None
    wa_id: str

class WhatsAppTextMessage(BaseModel):
    body: str

class WhatsAppInteractiveMessage(BaseModel):
    type: str # button_reply, list_reply
    button_reply: Optional[Dict[str, Any]] = None
    list_reply: Optional[Dict[str, Any]] = None

class WhatsAppIncomingMessage(BaseModel):
    from_number: str = Field(..., alias="from")
    id: str # wamid
    timestamp: str
    type: str # text, interactive, image, etc.
    text: Optional[WhatsAppTextMessage] = None
    interactive: Optional[WhatsAppInteractiveMessage] = None

class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: Dict[str, Any] # phone_number_id, display_phone_number
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppIncomingMessage]] = None

class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class MetaWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppEntry]


# =============================================================================
# CONVERSATION & MESSAGE REST DTO SCHEMAS
# =============================================================================

class MessageCreate(BaseModel):
    conversation_id: UUID
    wamid: Optional[str] = None
    sender_type: str # CUSTOMER, AI, HUMAN_AGENT, SYSTEM
    content: str
    meta_payload: Optional[Dict[str, Any]] = {}

class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    wamid: Optional[str]
    sender_type: str
    content: str
    meta_payload: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationOut(BaseModel):
    id: UUID
    tenant_id: UUID
    whatsapp_account_id: UUID
    customer_phone: str
    customer_name: Optional[str]
    status: str # AI_ACTIVE, AWAITING_CUSTOMER, HUMAN_ESCALATED, CLOSED
    assigned_user_id: Optional[UUID]
    last_activity_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class HandoffToggleRequest(BaseModel):
    action: str = Field(..., description="'takeover' to escalate to human, 'resume_ai' to re-enable AI")
