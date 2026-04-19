# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Auth dependencies for request context."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.exceptions import AuthError
from shared.security import decode_token

from auth_service.models.user import User

_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise AuthError("Missing authentication credentials")

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise AuthError("Invalid access token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Invalid access token")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise AuthError("User not found or inactive")

    return user
