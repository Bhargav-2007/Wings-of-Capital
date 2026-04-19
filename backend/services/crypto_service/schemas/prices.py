# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Price schemas for crypto service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class PriceQuote(BaseModel):
    symbol: str
    price: Decimal
    market_cap: Decimal
    volume_24h: Decimal
    last_updated: dt.datetime


class PricesResponse(BaseModel):
    currency: str
    data: List[PriceQuote]
