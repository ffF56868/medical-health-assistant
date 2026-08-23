"""Small Redis cache helpers used by the API.

Redis is an acceleration layer, not the source of truth. If Redis is
temporarily unavailable, the API falls back to MySQL and continues working.
"""

import json
import os
from typing import Any

from redis import Redis
from redis.exceptions import RedisError


def _positive_int_env(name: str, default: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if 1 <= value <= maximum else default


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_CACHE_ENABLED = os.getenv("REDIS_CACHE_ENABLED", "true").lower() == "true"
KNOWLEDGE_STATUS_CACHE_KEY = "medical-health:knowledge-status:v1"
KNOWLEDGE_STATUS_CACHE_TTL_SECONDS = _positive_int_env(
    "KNOWLEDGE_STATUS_CACHE_TTL_SECONDS",
    30,
    3600,
)
LOGIN_RATE_LIMIT_PER_MINUTE = _positive_int_env("LOGIN_RATE_LIMIT_PER_MINUTE", 30, 300)

redis_client: Redis = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
    health_check_interval=30,
)


def get_cached_json(key: str) -> Any | None:
    if not REDIS_CACHE_ENABLED:
        return None
    try:
        value = redis_client.get(key)
        return json.loads(value) if value is not None else None
    except (RedisError, TypeError, ValueError):
        return None


def set_cached_json(key: str, value: Any, ttl_seconds: int) -> bool:
    if not REDIS_CACHE_ENABLED:
        return False
    try:
        redis_client.setex(
            key,
            max(1, ttl_seconds),
            json.dumps(value, ensure_ascii=False, default=str),
        )
        return True
    except (RedisError, TypeError, ValueError):
        return False


def invalidate_knowledge_status_cache() -> bool:
    if not REDIS_CACHE_ENABLED:
        return False
    try:
        redis_client.delete(KNOWLEDGE_STATUS_CACHE_KEY)
        return True
    except (RedisError, AttributeError):
        return False


def check_redis() -> bool:
    if not REDIS_CACHE_ENABLED:
        return False
    try:
        return bool(redis_client.ping())
    except (RedisError, AttributeError):
        return False


def consume_fixed_window_limit(key: str, limit: int, window_seconds: int = 60) -> bool:
    """Return False when a short Redis-backed request window is exhausted.

    Redis is deliberately fail-open here. The permanent login lockout remains
    in MySQL, so a cache outage cannot turn into an outage of the login flow.
    """
    if not REDIS_CACHE_ENABLED:
        return True
    try:
        current_count = redis_client.incr(key)
        if current_count == 1:
            redis_client.expire(key, max(1, window_seconds))
        return current_count <= limit
    except (RedisError, AttributeError):
        return True
