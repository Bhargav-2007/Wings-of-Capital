# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Reporting utilities for ledger service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Dict, Iterable, Tuple

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from ledger_service.models.account import Account
from ledger_service.models.enums import AccountType, EntryType
from ledger_service.models.transaction import Transaction
from ledger_service.models.transaction_line import TransactionLine


def _to_datetime(value: dt.date, end_of_day: bool = False) -> dt.datetime:
    time_value = dt.time.max if end_of_day else dt.time.min
    return dt.datetime.combine(value, time_value, tzinfo=dt.timezone.utc)


def _aggregate_lines(
    db: Session,
    user_id: str,
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
) -> Dict[str, Tuple[Decimal, Decimal]]:
    debit_sum = func.coalesce(
        func.sum(case((TransactionLine.entry_type == EntryType.DEBIT, TransactionLine.amount), else_=0)),
        0,
    )
    credit_sum = func.coalesce(
        func.sum(case((TransactionLine.entry_type == EntryType.CREDIT, TransactionLine.amount), else_=0)),
        0,
    )

    query = (
        select(TransactionLine.account_id, debit_sum.label("debits"), credit_sum.label("credits"))
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .join(Account, Account.id == TransactionLine.account_id)
        .where(Account.user_id == user_id)
    )

    if start_date:
        query = query.where(Transaction.transaction_date >= _to_datetime(start_date))
    if end_date:
        query = query.where(Transaction.transaction_date <= _to_datetime(end_date, end_of_day=True))

    query = query.group_by(TransactionLine.account_id)

    rows = db.execute(query).all()
    return {str(row.account_id): (Decimal(row.debits), Decimal(row.credits)) for row in rows}


def _calculate_balance(account_type: AccountType, debits: Decimal, credits: Decimal) -> Decimal:
    if account_type in (AccountType.ASSET, AccountType.EXPENSE):
        return debits - credits
    return credits - debits


def trial_balance(
    db: Session,
    user_id: str,
    period_start: dt.date,
    period_end: dt.date,
) -> Tuple[list[Account], Dict[str, Decimal], Dict[str, Tuple[Decimal, Decimal]], Dict[str, Decimal]]:
    accounts = db.execute(
        select(Account).where(Account.user_id == user_id, Account.is_active.is_(True))
    ).scalars().all()

    opening_totals = _aggregate_lines(db, user_id, end_date=period_start - dt.timedelta(days=1))
    period_totals = _aggregate_lines(db, user_id, start_date=period_start, end_date=period_end)

    opening_balances: Dict[str, Decimal] = {}
    closing_balances: Dict[str, Decimal] = {}

    for account in accounts:
        opening_debits, opening_credits = opening_totals.get(str(account.id), (Decimal("0"), Decimal("0")))
        period_debits, period_credits = period_totals.get(str(account.id), (Decimal("0"), Decimal("0")))

        opening = _calculate_balance(account.account_type, opening_debits, opening_credits)
        closing = opening + _calculate_balance(account.account_type, period_debits, period_credits)

        opening_balances[str(account.id)] = opening
        closing_balances[str(account.id)] = closing

    return accounts, opening_balances, period_totals, closing_balances


def income_statement(
    db: Session,
    user_id: str,
    period_start: dt.date,
    period_end: dt.date,
) -> Tuple[Decimal, Decimal]:
    accounts = db.execute(
        select(Account).where(Account.user_id == user_id, Account.is_active.is_(True))
    ).scalars().all()

    period_map = _aggregate_lines(db, user_id, start_date=period_start, end_date=period_end)

    total_income = Decimal("0")
    total_expense = Decimal("0")

    for account in accounts:
        debits, credits = period_map.get(str(account.id), (Decimal("0"), Decimal("0")))
        balance = _calculate_balance(account.account_type, debits, credits)
        if account.account_type == AccountType.INCOME:
            total_income += balance
        elif account.account_type == AccountType.EXPENSE:
            total_expense += balance

    return total_income, total_expense


def balance_sheet(
    db: Session,
    user_id: str,
    as_of_date: dt.date | None = None,
) -> Tuple[Decimal, Decimal, Decimal]:
    accounts = db.execute(
        select(Account).where(Account.user_id == user_id, Account.is_active.is_(True))
    ).scalars().all()

    totals = {
        AccountType.ASSET: Decimal("0"),
        AccountType.LIABILITY: Decimal("0"),
        AccountType.EQUITY: Decimal("0"),
    }

    if as_of_date:
        # To compute balances "as of" a date, derive the account's balance at that
        # date by subtracting any net movement that occurred after the given date
        # from the account's current stored balance. This handles tests which
        # create accounts with an initial stored balance then post transactions
        # with historical dates.
        after_date = as_of_date + dt.timedelta(days=1)
        after_totals = _aggregate_lines(db, user_id, start_date=after_date)

        for account in accounts:
            after_debits, after_credits = after_totals.get(str(account.id), (Decimal("0"), Decimal("0")))
            net_after = _calculate_balance(account.account_type, after_debits, after_credits)
            # account.balance stores the current balance; subtract net movement
            # that happened after the as_of_date to get the historical balance.
            as_of_balance = Decimal(account.balance) - net_after
            if account.account_type in totals:
                totals[account.account_type] += as_of_balance
    else:
        for account in accounts:
            if account.account_type in totals:
                totals[account.account_type] += Decimal(account.balance)

    return totals[AccountType.ASSET], totals[AccountType.LIABILITY], totals[AccountType.EQUITY]
