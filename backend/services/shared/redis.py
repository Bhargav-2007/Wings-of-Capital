# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Redis client utilities with connection pooling."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from redis import ConnectionPool, Redis

from .config import get_settings

_settings = get_settings()


def _build_redis_url() -> str:
    env_url = os.getenv("REDIS_URL")
    env_password = os.getenv("REDIS_PASSWORD")
    env_ssl = os.getenv("REDIS_SSL")

    redis_url = env_url or _settings.redis_url
    redis_password = env_password or _settings.redis_password
    redis_ssl = (
        env_ssl.strip().lower() in {"1", "true", "yes", "on"}
        if env_ssl is not None
        else _settings.redis_ssl
    )

    if redis_password and "://" in redis_url and "@" not in redis_url:
        scheme, rest = redis_url.split("://", 1)
        redis_url = f"{scheme}://:{redis_password}@{rest}"

    if redis_ssl and redis_url.startswith("redis://"):
        redis_url = f"rediss://{redis_url[len('redis://'):] }"

    return redis_url


_pool: Optional[ConnectionPool] = None
_pool_url: Optional[str] = None


def _get_pool() -> ConnectionPool:
    global _pool, _pool_url, _pool_ssl

    redis_url = _build_redis_url()

    if _pool is None or _pool_url != redis_url:
        _pool = ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
        )
        _pool_url = redis_url
    return _pool


def get_redis_client() -> Redis:
    return Redis(connection_pool=_get_pool())


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
