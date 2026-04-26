# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Report routes for ledger service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from ledger_service.dependencies import get_current_user_id
from ledger_service.ledger.reporting import balance_sheet, income_statement, trial_balance
from ledger_service.schemas.reports import BalanceSheetReport, IncomeStatementReport, TrialBalanceReport, TrialBalanceRow
from shared.database import get_db

router = APIRouter(prefix="/api/v1/ledger/reports", tags=["reports"])


@router.get("/trial-balance", response_model=TrialBalanceReport)
def get_trial_balance(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    period_start: dt.date = Query(...),
    period_end: dt.date = Query(...),
) -> TrialBalanceReport:
    accounts, opening_map, period_totals, closing_map = trial_balance(db, user_id, period_start, period_end)

    rows = []
    total_debits = Decimal("0")
    total_credits = Decimal("0")

    for account in accounts:
        debits, credits = period_totals.get(str(account.id), (Decimal("0"), Decimal("0")))
        total_debits += debits
        total_credits += credits
        rows.append(
            TrialBalanceRow(
                account_id=str(account.id),
                account_number=account.account_number,
                account_name=account.account_name,
                account_type=account.account_type,
                currency=account.currency,
                opening_balance=opening_map.get(str(account.id), Decimal("0")),
                debit_total=debits,
                credit_total=credits,
                closing_balance=closing_map.get(str(account.id), Decimal("0")),
            )
        )

    return TrialBalanceReport(
        period_start=period_start,
        period_end=period_end,
        rows=rows,
        total_debits=total_debits,
        total_credits=total_credits,
    )


@router.get("/income-statement", response_model=IncomeStatementReport)
def get_income_statement(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    period_start: dt.date = Query(...),
    period_end: dt.date = Query(...),
) -> IncomeStatementReport:
    total_income, total_expense = income_statement(db, user_id, period_start, period_end)
    net_income = total_income - total_expense

    return IncomeStatementReport(
        period_start=period_start,
        period_end=period_end,
        total_income=total_income,
        total_expense=total_expense,
        net_income=net_income,
    )


@router.get("/balance-sheet", response_model=BalanceSheetReport)
def get_balance_sheet(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
    as_of_date: dt.date | None = Query(default=None),
) -> BalanceSheetReport:
    effective_date = as_of_date or dt.date.today()

    if as_of_date is None:
        # No date provided -> use the stored account balances (current state)
        total_assets, total_liabilities, total_equity = balance_sheet(db, user_id, None)
    else:
        # Date provided -> compute balances from transaction history up to that date
        total_assets, total_liabilities, total_equity = balance_sheet(db, user_id, as_of_date)

    return BalanceSheetReport(
        as_of_date=effective_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=total_equity,
    )
