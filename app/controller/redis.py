from fastapi import Request

async def set_redis(request: Request, key: str, value: str, ex: int) -> None:
    return await request.app.state.redis.set(key, value, ex=ex)

async def get_redis(request: Request, key: str) -> str:
    return await request.app.state.redis.get(key)

