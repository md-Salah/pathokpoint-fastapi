import redis.asyncio as aioredis
from app.config.settings import settings

async def get_redis():
    return await aioredis.from_url(settings.REDIS_URL,
                                   encoding="utf-8",
                                   decode_responses=True)
    
    
async def get_cache():
    return await aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )