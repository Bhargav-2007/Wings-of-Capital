# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""MFA models for TOTP secrets and backup codes."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class MfaSecret(BaseModel):
    __tablename__ = "mfa_secrets"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    secret_encrypted: Mapped[str] = mapped_column(String(512), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    backup_codes_salt: Mapped[str] = mapped_column(String(32), nullable=False)
    backup_codes_hashes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
