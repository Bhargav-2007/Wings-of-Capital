# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Password validation helpers."""

from __future__ import annotations

import re

from shared.config import get_settings
from shared.exceptions import ValidationError


_PASSWORD_RULES = [
    (re.compile(r"[A-Z]"), "an uppercase letter"),
    (re.compile(r"[a-z]"), "a lowercase letter"),
    (re.compile(r"\d"), "a number"),
    (re.compile(r"[^A-Za-z0-9]"), "a symbol"),
]


def validate_password_strength(password: str) -> None:
    settings = get_settings()
    if len(password) < settings.password_min_length:
        raise ValidationError(f"Password must be at least {settings.password_min_length} characters")

    for pattern, label in _PASSWORD_RULES:
        if not pattern.search(password):
            raise ValidationError(f"Password must include {label}")


def normalize_email(email: str) -> str:
    return email.strip().lower()
