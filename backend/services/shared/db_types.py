"""Database type helpers for cross-dialect compatibility.

Provides a `UUID` TypeDecorator that uses PostgreSQL's native UUID type when
available, and falls back to a fixed-length `String(36)` for SQLite/tests.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

try:
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
except Exception:  # pragma: no cover - runtime import guard
    PG_UUID = None


class UUID(TypeDecorator):
    """Cross-dialect UUID type.

    Uses PostgreSQL's native `UUID` when available; otherwise falls back to
    `String(36)`. Implements `load_dialect_impl` per SQLAlchemy recommendations
    so the class-level ``impl`` is present.
    """

    impl = String(36)
    cache_ok = True

    def __init__(self, as_uuid: bool = True):
        self.as_uuid = as_uuid
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and PG_UUID is not None:
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value: Any, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and PG_UUID is not None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value: Any, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and PG_UUID is not None:
            return value
        if self.as_uuid:
            try:
                return uuid.UUID(value)
            except Exception:
                return value
        return value
