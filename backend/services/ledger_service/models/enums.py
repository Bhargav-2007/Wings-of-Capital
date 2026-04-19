# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Ledger enums shared across models and schemas."""

from __future__ import annotations

from enum import Enum


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class EntryType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
