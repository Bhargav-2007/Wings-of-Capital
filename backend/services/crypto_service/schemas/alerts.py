# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Alert schemas for crypto service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import AnyUrl, BaseModel, EmailStr, Field

from crypto_service.models.enums import PriceAlertCondition


class PriceAlertCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=16)
    target_price: Decimal
    condition: PriceAlertCondition
    notify_email: EmailStr | None = None
    webhook_url: AnyUrl | None = None
    notify_on_trigger: bool = True


class PriceAlertOut(BaseModel):
    id: str
    symbol: str
    target_price: Decimal
    condition: PriceAlertCondition
    enabled: bool
    notify_email: EmailStr | None
    webhook_url: AnyUrl | None
    notify_on_trigger: bool
    triggered_at: dt.datetime | None
    last_notified_at: dt.datetime | None
    created_at: dt.datetime
