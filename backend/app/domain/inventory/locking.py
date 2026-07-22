import uuid
from typing import Optional
from contextlib import asynccontextmanager
import redis.asyncio as aioredis

from app.core.redis import RedisManager

class DistributedLockError(Exception):
    """Raised when an inventory lock cannot be acquired within timeout bounds."""
    pass

class RedisLockManager:
    """Manages Redis Distributed Locks (Redlock pattern) for concurrency protection."""

    @classmethod
    @asynccontextmanager
    async def acquire_inventory_lock(cls, tenant_id: uuid.UUID, sku: str, expire_seconds: int = 5):
        """Acquires atomic lock on SKU for a specific tenant."""
        redis = await RedisManager.get_redis()
        lock_key = f"lock:inventory:{tenant_id}:{sku.upper()}"
        token = str(uuid.uuid4())

        # SET NX EX
        acquired = await redis.set(lock_key, token, ex=expire_seconds, nx=True)
        if not acquired:
            raise DistributedLockError(f"High-volume lock contention for SKU '{sku}'. Please try again.")

        try:
            yield
        finally:
            # Atomic release using Lua script to prevent releasing another worker's lock
            lua_release = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            await redis.eval(lua_release, 1, lock_key, token)
