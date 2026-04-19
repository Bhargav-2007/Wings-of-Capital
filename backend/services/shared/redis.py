# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Redis client utilities with connection pooling."""

from __future__ import annotations

import json
from typing import Any, Optional

from redis import ConnectionPool, Redis

from .config import get_settings

_settings = get_settings()


def _build_redis_url() -> str:
    if _settings.redis_password and "://" in _settings.redis_url and "@" not in _settings.redis_url:
        scheme, rest = _settings.redis_url.split("://", 1)
        return f"{scheme}://:{_settings.redis_password}@{rest}"
    return _settings.redis_url


_pool = ConnectionPool.from_url(
    _build_redis_url(),
    decode_responses=True,
    ssl=_settings.redis_ssl,
)


def get_redis_client() -> Redis:
    return Redis(connection_pool=_pool)


class RedisClient:
    def __init__(self) -> None:
        self.client = get_redis_client()

    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
        return bool(self.client.set(name=key, value=value, ex=ttl_seconds))

    def delete(self, key: str) -> int:
        return int(self.client.delete(key))

    def incr(self, key: str, ttl_seconds: Optional[int] = None) -> int:
        value = self.client.incr(key)
        if ttl_seconds:
            self.client.expire(key, ttl_seconds)
        return int(value)

    def publish(self, channel: str, message: str) -> int:
        return int(self.client.publish(channel, message))

    def set_json(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        encoded = json.dumps(value)
        return self.set(key, encoded, ttl_seconds)

    def get_json(self, key: str) -> Optional[Any]:
        raw = self.get(key)
        if raw is None:
            return None
        return json.loads(raw)
