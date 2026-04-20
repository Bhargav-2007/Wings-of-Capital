# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""AI model metrics."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel


class AIModelMetric(BaseModel):
    __tablename__ = "ai_model_metrics"

    model_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("ai_models.id"), index=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(24, 12), nullable=False)
    dataset_symbol: Mapped[str | None] = mapped_column(String(16), nullable=True)
    dataset_start: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dataset_end: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dataset_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
