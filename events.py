import json
from .redis_conn import get_redis
CHANNEL="ymera:events"
async def publish(event: dict):
    r = await get_redis()
    await r.publish(CHANNEL, json.dumps(event))
