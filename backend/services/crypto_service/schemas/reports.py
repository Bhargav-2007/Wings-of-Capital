# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Crypto reporting schemas."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Dict, List

from pydantic import BaseModel


class PnlPosition(BaseModel):
    symbol: str
    quantity: Decimal
    cost_basis: Decimal
    current_price: Decimal
    current_value: Decimal
    pnl: Decimal
    pnl_percent: Decimal


class PnlSummary(BaseModel):
    total_value: Decimal
    total_cost: Decimal
    total_pnl: Decimal
    pnl_percent: Decimal
    positions: List[PnlPosition]


class PnlHistoryPoint(BaseModel):
    date: dt.date
    total_value: Decimal
    total_cost: Decimal
    total_pnl: Decimal
    pnl_percent: Decimal


class PnlHistoryResponse(BaseModel):
    currency: str
    points: List[PnlHistoryPoint]


class AllocationPoint(BaseModel):
    date: dt.date
    total_value: Decimal
    allocation: Dict[str, Decimal]


class AllocationHistoryResponse(BaseModel):
    currency: str
    points: List[AllocationPoint]
