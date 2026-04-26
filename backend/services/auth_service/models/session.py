# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Session model for refresh token tracking."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, String
from shared.db_types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class Session(BaseModel):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
