# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Transaction model for ledger journal entries."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, String
from shared.db_types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class Transaction(BaseModel):
    __tablename__ = "transactions"

    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transaction_date: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    posted_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
