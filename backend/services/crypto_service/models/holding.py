# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Holdings model for crypto portfolios."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from shared.db_types import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class Holding(BaseModel):
    __tablename__ = "holdings"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    acquired_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
