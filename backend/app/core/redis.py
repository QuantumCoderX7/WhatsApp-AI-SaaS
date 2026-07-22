import redis.asyncio as aioredis
from typing import Optional
from app.core.config import settings

class RedisManager:
    _redis: Optional[aioredis.Redis] = None

    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        """Returns or initializes the async Redis client instance."""
        if cls._redis is None:
            cls._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._redis

    @classmethod
    async def close_redis(cls):
        """Closes the Redis connection pool on application shutdown."""
        if cls._redis is not None:
            await cls._redis.close()
            cls._redis = None

async def get_redis_client() -> aioredis.Redis:
    """FastAPI dependency for accessing Redis."""
    return await RedisManager.get_redis()
