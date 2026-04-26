# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Trial balance snapshot model for reporting."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric
from shared.db_types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class TrialBalance(BaseModel):
    __tablename__ = "trial_balances"

    account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), index=True, nullable=False)
    period_start: Mapped[dt.date] = mapped_column(Date, nullable=False)
    period_end: Mapped[dt.date] = mapped_column(Date, nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    debit_total: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    credit_total: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    calculated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc), nullable=False
    )
