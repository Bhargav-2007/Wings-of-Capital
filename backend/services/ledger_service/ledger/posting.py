# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Transaction posting logic for the ledger service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ledger_service.models.account import Account
from ledger_service.models.enums import AccountType, EntryType
from ledger_service.models.transaction import Transaction
from ledger_service.models.transaction_line import TransactionLine
from ledger_service.schemas.transactions import TransactionCreate, TransactionLineIn
from shared.exceptions import AuthError, ValidationError

_DECIMAL_PLACES = Decimal("0.00000001")


def _normalize_amount(amount: Decimal) -> Decimal:
    return amount.quantize(_DECIMAL_PLACES, rounding=ROUND_HALF_UP)


def _apply_entry(account_type: AccountType, entry_type: EntryType, amount: Decimal) -> Decimal:
    if account_type in (AccountType.ASSET, AccountType.EXPENSE):
        return amount if entry_type == EntryType.DEBIT else -amount
    return amount if entry_type == EntryType.CREDIT else -amount


def _validate_balancing(lines: Iterable[TransactionLineIn]) -> tuple[Decimal, Decimal]:
    debit_total = Decimal("0")
    credit_total = Decimal("0")

    for line in lines:
        amount = _normalize_amount(line.amount)
        if line.entry_type == EntryType.DEBIT:
            debit_total += amount
        else:
            credit_total += amount

    if debit_total != credit_total:
        raise ValidationError("Transaction does not balance")

    return debit_total, credit_total


def _load_accounts(db: Session, account_ids: List[str]) -> Dict[str, Account]:
    accounts = db.execute(
        select(Account).where(Account.id.in_(account_ids)).with_for_update()
    ).scalars().all()
    if len(accounts) != len(set(account_ids)):
        raise ValidationError("One or more accounts are invalid")
    return {str(account.id): account for account in accounts}


def _validate_currency(lines: Iterable[TransactionLineIn], accounts: Dict[str, Account]) -> str:
    currency = None
    for line in lines:
        account = accounts[str(line.account_id)]
        if line.currency and line.currency != account.currency:
            raise ValidationError("Transaction line currency mismatch")
        currency = currency or account.currency
        if account.currency != currency:
            raise ValidationError("Multi-currency transactions require FX handling")
    return currency or "USD"


def post_transaction(db: Session, payload: TransactionCreate, user_id: str) -> Transaction:
    if len(payload.lines) < 2:
        raise ValidationError("Transaction must include at least two lines")

    _validate_balancing(payload.lines)

    account_ids = [line.account_id for line in payload.lines]
    accounts = _load_accounts(db, account_ids)
    _validate_currency(payload.lines, accounts)

    for account in accounts.values():
        if str(account.user_id) != str(user_id):
            raise AuthError("Account ownership mismatch")
        if not account.is_active:
            raise ValidationError("Account is inactive")

    now = dt.datetime.now(dt.timezone.utc)
    transaction_date = payload.transaction_date or now

    transaction = Transaction(
        description=payload.description,
        reference=payload.reference,
        transaction_date=transaction_date,
        posted_at=now,
        created_by=user_id,
    )
    db.add(transaction)
    db.flush()

    for line in payload.lines:
        account = accounts[str(line.account_id)]
        amount = _normalize_amount(line.amount)
        delta = _apply_entry(account.account_type, line.entry_type, amount)
        new_balance = _normalize_amount(account.balance + delta)
        if not account.allow_negative and new_balance < Decimal("0"):
            raise ValidationError("Insufficient balance for account")

        account.balance = new_balance

        db.add(
            TransactionLine(
                transaction_id=transaction.id,
                account_id=account.id,
                entry_type=line.entry_type,
                amount=amount,
                currency=account.currency,
                memo=line.memo,
                posted_at=now,
            )
        )

    db.commit()
    db.refresh(transaction)
    return transaction
