from functools import lru_cache

from app.core.config import settings


def _get_redis_url() -> str:
    return settings.REDIS_URL.strip() if settings.REDIS_URL else ""


@lru_cache()
def get_redis_client():
    """Get Redis client, only if REDIS_URL is configured."""
    redis_url = _get_redis_url()
    if not redis_url:
        return None
    import redis.asyncio as redis
    return redis.from_url(redis_url, decode_responses=True)


redis_client = get_redis_client()


async def get_redis():
    """Get Redis client instance.
    
    Returns None if Redis is not configured or available.
    """
    return redis_client
