# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Token helpers for email verification."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from jose import JWTError, jwt

from shared.config import get_settings
from shared.exceptions import AuthError


def create_verification_token(subject: str, expires_hours: int = 24) -> str:
    settings = get_settings()
    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=expires_hours)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": "verify",
        "exp": expire,
        "iat": dt.datetime.now(dt.timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_signing_key, algorithm=settings.jwt_algorithm)


def decode_verification_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_verification_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthError("Invalid or expired verification token") from exc

    if payload.get("type") != "verify":
        raise AuthError("Invalid verification token")

    return payload
