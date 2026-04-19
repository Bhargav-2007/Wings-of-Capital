# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Market price history model."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class MarketPrice(BaseModel):
    __tablename__ = "market_prices"

    symbol: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    price_usd: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    volume_24h: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    market_cap: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
