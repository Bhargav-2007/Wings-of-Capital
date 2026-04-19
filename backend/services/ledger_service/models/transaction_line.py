# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Transaction lines representing debits and credits."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel

from .enums import EntryType


class TransactionLine(BaseModel):
    __tablename__ = "transaction_lines"

    transaction_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), index=True, nullable=False
    )
    account_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), index=True, nullable=False
    )
    entry_type: Mapped[EntryType] = mapped_column(sa.Enum(EntryType, name="entry_type"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
