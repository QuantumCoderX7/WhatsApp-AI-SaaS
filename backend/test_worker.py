import asyncio
import traceback
from app.workers.tasks_webhook import process_whatsapp_webhook_task

payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "1048900694241631",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "923392208970",
                    "phone_number_id": "1298976603289591"
                },
                "contacts": [{"profile": {"name": "Rayyan Asim"}, "wa_id": "923072208970"}],
                "messages": [{
                    "from": "923072208970",
                    "id": "wamid.TEST_923072208970_001",
                    "timestamp": "1784751300",
                    "text": {"body": "hello from 923072208970"},
                    "type": "text"
                }]
            },
            "field": "messages"
        }]
    }]
}

async def main():
    print("Testing process_whatsapp_webhook_task directly for 923072208970...")
    try:
        await process_whatsapp_webhook_task({}, payload)
        print("WORKER PROCESS COMPLETED CLEANLY.")
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
