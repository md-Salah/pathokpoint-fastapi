from fastapi import Request
import logging
import traceback

from app.controller.exception import ServerErrorException

logger = logging.getLogger(__name__)


async def set_redis(request: Request, key: str, value: str, ex: int) -> None:
    try:
        return await request.app.state.redis.set(key, value, ex=ex)
    except Exception:
        logger.error(traceback.format_exc())
        raise ServerErrorException(
            "Something went wrong, please try again later.")


async def get_redis(request: Request, key: str) -> str | None:
    try:
        return await request.app.state.redis.get(key)
    except Exception:
        logger.error(traceback.format_exc())
        raise ServerErrorException(
            "Something went wrong, please try again later.")


async def delete_redis(request: Request, key: str) -> None:
    try:
        return await request.app.state.redis.delete(key)
    except Exception:
        logger.error(traceback.format_exc())
        raise ServerErrorException(
            "Something went wrong, please try again later.")
