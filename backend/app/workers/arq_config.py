from arq.connections import RedisSettings
from app.core.config import settings
from app.workers.tasks_webhook import process_whatsapp_webhook_task

class WorkerSettings:
    """ARQ Task Worker Configuration Settings."""
    functions = [process_whatsapp_webhook_task]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD or None,
        ssl=settings.REDIS_SSL
    )
    max_jobs = 50
    job_timeout = 60
