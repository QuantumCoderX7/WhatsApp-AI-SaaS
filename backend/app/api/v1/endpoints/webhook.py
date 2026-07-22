import json
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends, Query, BackgroundTasks
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.security import verify_meta_signature
from app.core.redis import get_redis_client
from app.workers.tasks_webhook import process_whatsapp_webhook_task

router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook_hub(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    """Meta Webhook Verification Challenge Endpoint."""
    if mode == "subscribe" and token == settings.META_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch"
    )

@router.post("/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    redis: aioredis.Redis = Depends(get_redis_client)
):
    """Inbound WhatsApp Event Stream Endpoint from Meta Cloud API."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # 1. Security Check (HMAC-SHA256 Signature Validation)
    if settings.ENVIRONMENT == "production":
        if not verify_meta_signature(body, signature, settings.META_APP_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Meta signature"
            )

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # 2. Extract Message ID for Redis Deduplication
    entries = payload.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            for msg in messages:
                wamid = msg.get("id")
                if wamid:
                    redis_key = f"whatsapp:msg:{wamid}"
                    # SET NX EX (24 hours TTL)
                    is_new = await redis.set(redis_key, "processed", ex=86400, nx=True)
                    if not is_new:
                        print(f"Duplicate message ignored: {wamid}")
                        return {"status": "duplicate_ignored"}

    # 3. Enqueue Job to Background Task Runner (Fast 200 OK Response)
    background_tasks.add_task(process_whatsapp_webhook_task, {}, payload)

    return {"status": "enqueued"}
