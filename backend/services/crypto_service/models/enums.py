# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Crypto service enums."""

from __future__ import annotations

from enum import Enum


class PriceAlertCondition(str, Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"


class AIModelStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
