# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Prediction schemas for crypto service."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=16)
    horizon_days: int = Field(default=7, ge=1, le=365)


class PredictionResponse(BaseModel):
    symbol: str
    horizon_days: int
    forecast: Decimal
    confidence_interval: List[Decimal]
    model_version: str
