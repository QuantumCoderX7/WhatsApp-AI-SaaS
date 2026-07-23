import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

# Placeholder tokens that should trigger fallback to .env
_PLACEHOLDER_TOKENS = {"YOUR_ACCESS_TOKEN", "mock_token", "CHANGE_ME", ""}

class WhatsAppOutboundService:
    """Service for sending text & interactive messages via Meta WhatsApp Cloud API."""

    @classmethod
    def _is_placeholder(cls, token: Optional[str]) -> bool:
        """Check if a token is a placeholder / not a real Meta access token."""
        if not token:
            return True
        return token.strip() in _PLACEHOLDER_TOKENS or token.startswith("mock_")

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
        1. Uses provided access_token (if DB tenant token is real).
        2. Falls back to META_ACCESS_TOKEN from .env (for temporary dev tokens or global tokens).
        3. If both are placeholders, runs in mock mode.
        """
        # Smart token resolution: skip placeholder tokens
        if cls._is_placeholder(access_token):
            token = settings.META_ACCESS_TOKEN
            print(f"[Outbound] DB token is placeholder, using .env META_ACCESS_TOKEN")
        else:
            token = access_token

        # Final check: if even .env token is placeholder, use mock mode
        if cls._is_placeholder(token):
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

        print(f"[Outbound] Calling Meta API: {url}")
        print(f"[Outbound] Recipient: {recipient_phone} | Token prefix: {token[:20]}...")

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            print(f"[Outbound] Meta API Response: {response.status_code} | {response.text}")
            if response.status_code in (200, 201):
                print(f"[Meta WhatsApp Outbound SUCCESS] Sent to {recipient_phone}")
                return response.json()
            else:
                print(f"[Meta WhatsApp Outbound ERROR] Status: {response.status_code} | Body: {response.text}")
                return None
