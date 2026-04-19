# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""AI model registry."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.models import BaseModel

from .enums import AIModelStatus


class AIModel(BaseModel):
    __tablename__ = "ai_models"

    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    accuracy: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=0)
    deployment_date: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AIModelStatus] = mapped_column(sa.Enum(AIModelStatus, name="ai_model_status"), nullable=False)
