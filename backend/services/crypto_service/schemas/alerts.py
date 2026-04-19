# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Alert schemas for crypto service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, Field

from crypto_service.models.enums import PriceAlertCondition


class PriceAlertCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=16)
    target_price: Decimal
    condition: PriceAlertCondition


class PriceAlertOut(BaseModel):
    id: str
    symbol: str
    target_price: Decimal
    condition: PriceAlertCondition
    enabled: bool
    triggered_at: dt.datetime | None
    created_at: dt.datetime
