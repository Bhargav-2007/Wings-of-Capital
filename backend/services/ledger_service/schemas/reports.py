# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Report schemas for ledger service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from ledger_service.models.enums import AccountType


class TrialBalanceRow(BaseModel):
    account_id: str
    account_number: str
    account_name: str
    account_type: AccountType
    currency: str
    opening_balance: Decimal
    debit_total: Decimal
    credit_total: Decimal
    closing_balance: Decimal


class TrialBalanceReport(BaseModel):
    period_start: dt.date
    period_end: dt.date
    rows: List[TrialBalanceRow]
    total_debits: Decimal
    total_credits: Decimal


class IncomeStatementReport(BaseModel):
    period_start: dt.date
    period_end: dt.date
    total_income: Decimal
    total_expense: Decimal
    net_income: Decimal


class BalanceSheetReport(BaseModel):
    as_of_date: dt.date
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
