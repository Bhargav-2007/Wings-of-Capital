# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Portfolio schemas for crypto service."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from pydantic import BaseModel


class PortfolioHolding(BaseModel):
    symbol: str
    quantity: Decimal
    cost_basis: Decimal
    current_price: Decimal
    current_value: Decimal
    pnl: Decimal
    pnl_percent: Decimal


class PortfolioResponse(BaseModel):
    total_value: Decimal
    total_cost: Decimal
    total_pnl: Decimal
    allocation: Dict[str, Decimal]
    holdings: List[PortfolioHolding]
