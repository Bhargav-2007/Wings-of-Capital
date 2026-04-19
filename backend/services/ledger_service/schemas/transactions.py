# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Transaction schemas for ledger service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ledger_service.models.enums import EntryType


class TransactionLineIn(BaseModel):
    account_id: str
    entry_type: EntryType
    amount: Decimal = Field(gt=0)
    memo: Optional[str] = Field(default=None, max_length=255)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)


class TransactionCreate(BaseModel):
    description: Optional[str] = Field(default=None, max_length=512)
    reference: Optional[str] = Field(default=None, max_length=64)
    transaction_date: Optional[dt.datetime] = None
    lines: List[TransactionLineIn] = Field(min_length=2)


class TransactionLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    entry_type: EntryType
    amount: Decimal
    currency: str
    memo: Optional[str]
    posted_at: dt.datetime


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    description: Optional[str]
    reference: Optional[str]
    transaction_date: dt.datetime
    posted_at: dt.datetime
    created_by: str
    lines: List[TransactionLineOut]
