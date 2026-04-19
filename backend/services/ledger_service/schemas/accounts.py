# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Account schemas for ledger service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ledger_service.models.enums import AccountType


class AccountCreate(BaseModel):
    account_number: str = Field(min_length=3, max_length=32)
    account_name: str = Field(min_length=2, max_length=255)
    account_type: AccountType
    currency: str = Field(min_length=3, max_length=3)
    allow_negative: bool = False


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_number: str
    account_name: str
    account_type: AccountType
    currency: str
    balance: Decimal
    allow_negative: bool
    is_active: bool
    created_at: dt.datetime


class BalanceResponse(BaseModel):
    account_id: str
    balance: Decimal
    as_of_date: dt.datetime
    currency: str
