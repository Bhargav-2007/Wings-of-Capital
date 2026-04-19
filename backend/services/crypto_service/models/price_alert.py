# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Price alert model."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel

from .enums import PriceAlertCondition


class PriceAlert(BaseModel):
    __tablename__ = "price_alerts"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    target_price: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    condition: Mapped[PriceAlertCondition] = mapped_column(
        sa.Enum(PriceAlertCondition, name="price_alert_condition"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    triggered_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
