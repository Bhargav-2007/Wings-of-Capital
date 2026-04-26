# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Authentication, JWT, and security utilities."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings
from .exceptions import AuthError, RateLimitError
from .redis import RedisClient

_settings = get_settings()
# Use PBKDF2-SHA256 to avoid bcrypt binary/version issues in test environments
_pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=_settings.bcrypt_rounds,
)


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, claims: Optional[Dict[str, Any]] = None) -> str:
    return _create_token(subject, "access", _settings.jwt_expiry_minutes, claims)


def create_refresh_token(subject: str, claims: Optional[Dict[str, Any]] = None) -> str:
    return _create_token(subject, "refresh", _settings.jwt_refresh_expiry_days * 24 * 60, claims)


def _create_token(subject: str, token_type: str, expires_minutes: int, claims: Optional[Dict[str, Any]]) -> str:
    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=expires_minutes)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
        "iat": dt.datetime.now(dt.timezone.utc),
    }
    if claims:
        payload.update(claims)
    return jwt.encode(payload, _settings.jwt_signing_key, algorithm=_settings.jwt_algorithm)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, _settings.jwt_verification_key, algorithms=[_settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthError("Invalid or expired token") from exc


def apply_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.allowed_origins,
        allow_credentials=_settings.cors_allow_credentials,
        allow_methods=_settings.cors_methods_list,
        allow_headers=_settings.cors_headers_list,
    )


def add_security_headers(response: Any) -> Any:
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


class RateLimiter:
    def __init__(self, redis_client: Optional[RedisClient] = None) -> None:
        self.redis = redis_client or RedisClient()
        self.enabled = _settings.rate_limit_enabled
        self.limit = _settings.rate_limit_per_ip
        self.window_seconds = _settings.rate_limit_window_seconds

    def is_allowed(self, key: str, limit: Optional[int] = None, window_seconds: Optional[int] = None) -> bool:
        if not self.enabled:
            return True
        limit = limit or self.limit
        window_seconds = window_seconds or self.window_seconds

        count = self.redis.client.incr(key)
        if count == 1:
            self.redis.client.expire(key, window_seconds)
        return count <= limit

    def enforce(self, key: str, limit: Optional[int] = None, window_seconds: Optional[int] = None) -> None:
        if not self.is_allowed(key, limit, window_seconds):
            raise RateLimitError()
