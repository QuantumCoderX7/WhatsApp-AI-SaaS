import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class WhatsAppOutboundService:
    """Service for sending text & interactive messages via Meta WhatsApp Cloud API."""

    @classmethod
    async def send_text_message(
        cls,
        phone_number_id: str,
        access_token: Optional[str],
        recipient_phone: str,
        text_body: str
    ) -> Optional[Dict[str, Any]]:
        """Dispatches an outbound text message to a customer's WhatsApp.
        
        Token Resolution:
        1. Uses provided access_token (if DB tenant token exists).
        2. Falls back to META_ACCESS_TOKEN from .env (for temporary dev tokens or global tokens).
        """
        token = access_token or settings.META_ACCESS_TOKEN

        # If running in local mock dev mode without any token configured
        if not token or token == "YOUR_ACCESS_TOKEN" or token.startswith("mock_"):
            print(f"[Mock WhatsApp Outbound] To: {recipient_phone} | Body: {text_body}")
            return {"messaging_product": "whatsapp", "messages": [{"id": "wamid.MOCK_OUTBOUND_123"}]}

        # Target Meta Graph API version and endpoint
        api_version = settings.META_API_VERSION or "v18.0"
        target_phone_id = phone_number_id or settings.META_PHONE_NUMBER_ID
        
        url = f"https://graph.facebook.com/{api_version}/{target_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text_body
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in (200, 201):
                print(f"[Meta WhatsApp Outbound SUCCESS] Sent to {recipient_phone}")
                return response.json()
            else:
                print(f"[Meta WhatsApp Outbound ERROR] Status: {response.status_code} | Body: {response.text}")
                return None
