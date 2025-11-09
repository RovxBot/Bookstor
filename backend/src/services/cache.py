"""Redis caching utilities (optional).

Provides lightweight async helpers for caching merged ISBN lookups
and (future) series gap computations. If Redis is not configured, all
functions gracefully no-op.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

try:
    import redis.asyncio as redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore

logger = logging.getLogger("bookstor.cache")

from typing import Any
_redis_client: Optional[Any] = None


def get_redis_url() -> Optional[str]:
    # Environment variable name choice; can be extended to settings later
    import os
    return os.getenv("REDIS_URL") or os.getenv("CACHE_URL")


def get_client() -> Optional[Any]:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if redis is None:
        logger.info("Redis library not available; caching disabled")
        return None
    url = get_redis_url()
    if not url:
        logger.info("No REDIS_URL provided; caching disabled")
        return None
    try:
        _redis_client = redis.Redis.from_url(url, decode_responses=True)
    except Exception as e:  # pragma: no cover
        logger.error("Failed to create Redis client: %s", e)
        _redis_client = None
    return _redis_client


def isbn_cache_key(isbn: str) -> str:
    return f"bookstor:isbn:{isbn.strip()}"


async def cache_get_isbn(isbn: str) -> Optional[dict]:
    client = get_client()
    if not client:
        return None
    try:
        data = await client.get(isbn_cache_key(isbn))
        if data:
            return json.loads(data)
    except Exception as e:  # pragma: no cover
        logger.warning("Redis get failed for %s: %s", isbn, e)
    return None


async def cache_set_isbn(isbn: str, payload: dict, ttl: int = 3600) -> None:
    client = get_client()
    if not client:
        return
    try:
        await client.set(isbn_cache_key(isbn), json.dumps(payload), ex=ttl)
    except Exception as e:  # pragma: no cover
        logger.warning("Redis set failed for %s: %s", isbn, e)
