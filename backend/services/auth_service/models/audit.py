# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Audit log entries for authentication events."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from shared.db_types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class AuthAuditLog(BaseModel):
    __tablename__ = "auth_audit_logs"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
