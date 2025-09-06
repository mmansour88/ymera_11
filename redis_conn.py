import os, redis.asyncio as redis
_redis=None
async def get_redis():
    global _redis
    if _redis is None:
        _redis = redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))
    return _redis
