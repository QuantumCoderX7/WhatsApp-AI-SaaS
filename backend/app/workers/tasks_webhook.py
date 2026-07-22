from typing import Dict, Any
from uuid import UUID
from sqlalchemy import select, text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.domain.tenant.models import Tenant, User
from app.domain.conversation.models import WhatsAppAccount
from app.domain.conversation.repository import ConversationRepository
from app.domain.conversation.state_machine import ConversationState
from app.domain.ai.gemini_client import GeminiClient
from app.domain.conversation.outbound import WhatsAppOutboundService

async def process_whatsapp_webhook_task(ctx: Dict[str, Any], payload: Dict[str, Any]):
    """ARQ Background Worker task for processing inbound WhatsApp messages & AI turns."""
    print("Processing inbound WhatsApp payload in background worker...")
    
    entries = payload.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id") or settings.META_PHONE_NUMBER_ID
            
            if not phone_number_id:
                continue
                
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])
            contact_name = contacts[0].get("profile", {}).get("name") if contacts else None
            
            async with AsyncSessionLocal() as session:
                repo = ConversationRepository(session)
                
                # 1. Resolve WhatsApp account & Tenant ID
                wa_account = await repo.get_whatsapp_account_by_phone_number_id(phone_number_id)
                
                # Auto-provision default WhatsApp Account for dev testing if missing
                if not wa_account:
                    # Check or create default tenant
                    tenant_stmt = select(Tenant).limit(1)
                    res = await session.execute(tenant_stmt)
                    tenant = res.scalar_one_or_none()

                    if not tenant:
                        tenant = Tenant(name="Demo Business", slug="demo-business", plan_tier="starter")
                        session.add(tenant)
                        await session.flush()

                    wa_account = WhatsAppAccount(
                        tenant_id=tenant.id,
                        phone_number_id=phone_number_id,
                        waba_id=settings.META_WABA_ID or "default_waba",
                        display_phone_number=settings.META_BUSINESS_PHONE_NUMBER if hasattr(settings, 'META_BUSINESS_PHONE_NUMBER') else "WhatsApp Business",
                        access_token_encrypted=settings.META_ACCESS_TOKEN,
                        webhook_verify_token=settings.META_VERIFY_TOKEN
                    )
                    session.add(wa_account)
                    await session.flush()
                    await session.commit()
                    # Re-fetch with relationship
                    wa_account = await repo.get_whatsapp_account_by_phone_number_id(phone_number_id)
                    
                tenant_id = wa_account.tenant_id
                
                # Bind RLS session context if PostgreSQL
                if not settings.DATABASE_URL.startswith("sqlite"):
                    await session.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'"))
                
                for msg in messages:
                    customer_phone = msg.get("from")
                    wamid = msg.get("id")
                    msg_type = msg.get("type")
                    
                    content = ""
                    if msg_type == "text":
                        content = msg.get("text", {}).get("body", "")
                    elif msg_type == "interactive":
                        interactive = msg.get("interactive", {})
                        if interactive.get("type") == "button_reply":
                            content = interactive.get("button_reply", {}).get("title", "")
                        elif interactive.get("type") == "list_reply":
                            content = interactive.get("list_reply", {}).get("title", "")
                    else:
                        content = f"[{msg_type.upper()} Attachment]"

                    if not content:
                        continue

                    # 2. Fetch or Create Conversation
                    conversation = await repo.get_by_customer_phone(tenant_id, customer_phone)
                    if not conversation:
                        conversation = await repo.create_conversation(
                            tenant_id=tenant_id,
                            whatsapp_account_id=wa_account.id,
                            customer_phone=customer_phone,
                            customer_name=contact_name
                        )
                    
                    # 3. Append Customer Message
                    await repo.append_message(
                        tenant_id=tenant_id,
                        conversation_id=conversation.id,
                        sender_type="CUSTOMER",
                        content=content,
                        wamid=wamid,
                        meta_payload=msg
                    )

                    # 4. Check State: If HUMAN_ESCALATED, do not trigger AI turn
                    if conversation.status == ConversationState.HUMAN_ESCALATED.value:
                        print(f"Conversation {conversation.id} is HUMAN_ESCALATED. Skipping AI turn.")
                        await session.commit()
                        continue

                    # 5. Load Recent Chat History (Last 10 messages)
                    raw_history = await repo.get_recent_messages(conversation.id, limit=10)
                    formatted_history = [
                        {"sender_type": m.sender_type, "content": m.content}
                        for m in raw_history[:-1] # Exclude current message
                    ]

                    # 6. Execute Gemini AI Turn Loop (with tool calling execution)
                    gemini_client = GeminiClient()
                    ai_response_text = await gemini_client.generate_response_with_tools(
                        db=session,
                        tenant_id=tenant_id,
                        conversation_id=conversation.id,
                        chat_history=formatted_history,
                        user_message=content,
                        business_name=wa_account.tenant.name if wa_account.tenant else "Our Store"
                    )

                    # 7. Persist AI Response Message
                    await repo.append_message(
                        tenant_id=tenant_id,
                        conversation_id=conversation.id,
                        sender_type="AI",
                        content=ai_response_text
                    )

                    # Update status to AWAITING_CUSTOMER if AI response dispatched
                    if conversation.status != ConversationState.HUMAN_ESCALATED.value:
                        await repo.update_status(conversation.id, ConversationState.AWAITING_CUSTOMER.value)

                    await session.commit()

                    # 8. Dispatch Outbound Text Message via Meta WhatsApp API (using token from .env or DB)
                    await WhatsAppOutboundService.send_text_message(
                        phone_number_id=wa_account.phone_number_id,
                        access_token=wa_account.access_token_encrypted or settings.META_ACCESS_TOKEN,
                        recipient_phone=customer_phone,
                        text_body=ai_response_text
                    )

                    print(f"Successfully completed AI turn & dispatched response to {customer_phone}")
