import asyncio
from app.domain.conversation.outbound import WhatsAppOutboundService
from app.core.config import settings

async def main():
    print(f"Sending test WhatsApp message to +923072208970 via Phone Number ID: {settings.META_PHONE_NUMBER_ID}...")
    res = await WhatsAppOutboundService.send_text_message(
        phone_number_id=settings.META_PHONE_NUMBER_ID,
        access_token=settings.META_ACCESS_TOKEN,
        recipient_phone="923072208970",
        text_body="Hello from WhatsApp AI SaaS Platform! Your server is connected."
    )
    print("Meta API Response:", res)

if __name__ == "__main__":
    asyncio.run(main())
