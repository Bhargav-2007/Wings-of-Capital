# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Crypto service dependencies."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.exceptions import AuthError
from shared.security import decode_token

_security = HTTPBearer(auto_error=False)


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(_security)) -> str:
    if not credentials:
        raise AuthError("Missing authentication credentials")

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise AuthError("Invalid access token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Invalid access token")

    return str(user_id)
