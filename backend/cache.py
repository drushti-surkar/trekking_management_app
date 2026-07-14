import json

import redis
from flask import current_app

_client = None

OPEN_TREKS_KEY = "treks:open"


def _r():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(
            current_app.config["CACHE_REDIS_URL"], decode_responses=True
        )
    return _client


def cache_get(key):
    try:
        raw = _r().get(key)
        return json.loads(raw) if raw else None
    except Exception as e:  # never let a cache issue break the request
        current_app.logger.warning(f"cache_get failed: {e}")
        return None


def cache_set(key, value, ttl=None):
    try:
        ttl = ttl or current_app.config.get("CACHE_TTL", 60)
        _r().set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        current_app.logger.warning(f"cache_set failed: {e}")


def invalidate_open_treks():
    """Call after any change that affects the open-trek listing."""
    try:
        _r().delete(OPEN_TREKS_KEY)
    except Exception as e:
        current_app.logger.warning(f"cache invalidate failed: {e}")
