# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""AI model schemas."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from uuid import UUID

from shared.schemas import BaseSchema
from crypto_service.models.enums import AIModelStatus


class AIModelOut(BaseSchema):
    id: UUID
    model_name: str
    version: str
    accuracy: Decimal
    deployment_date: dt.datetime
    status: AIModelStatus


class AIModelMetricOut(BaseSchema):
    id: UUID
    model_id: UUID
    metric_name: str
    metric_value: Decimal
    dataset_symbol: str | None
    dataset_start: dt.datetime | None
    dataset_end: dt.datetime | None
    dataset_size: int
    created_at: dt.datetime
