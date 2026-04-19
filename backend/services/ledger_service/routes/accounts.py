# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Account routes for ledger service."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ledger_service.dependencies import get_current_user_id
from ledger_service.models.account import Account
from ledger_service.models.enums import AccountType
from ledger_service.schemas.accounts import AccountCreate, AccountOut, BalanceResponse
from shared.database import get_db
from shared.exceptions import ConflictError, NotFoundError
from shared.schemas import PaginatedResponse

router = APIRouter(prefix="/api/v1/ledger/accounts", tags=["accounts"])


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AccountOut:
    existing = db.execute(
        select(Account).where(
            Account.user_id == user_id,
            Account.account_number == payload.account_number,
        )
    ).scalar_one_or_none()

    if existing:
        raise ConflictError("Account number already exists")

    account = Account(
        user_id=user_id,
        account_number=payload.account_number,
        account_name=payload.account_name,
        account_type=payload.account_type,
        currency=payload.currency.upper(),
        balance=0,
        allow_negative=payload.allow_negative,
        is_active=True,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return AccountOut.model_validate(account)


@router.get("", response_model=PaginatedResponse[AccountOut])
def list_accounts(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    currency: Optional[str] = Query(default=None, min_length=3, max_length=3),
    account_type: Optional[AccountType] = None,
) -> PaginatedResponse[AccountOut]:
    query = select(Account).where(Account.user_id == user_id)
    if currency:
        query = query.where(Account.currency == currency.upper())
    if account_type:
        query = query.where(Account.account_type == account_type)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

    accounts = db.execute(query.offset(skip).limit(limit)).scalars().all()
    items = [AccountOut.model_validate(account) for account in accounts]

    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{account_id}/balance", response_model=BalanceResponse)
def get_balance(
    account_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> BalanceResponse:
    account = db.get(Account, account_id)
    if not account or str(account.user_id) != str(user_id):
        raise NotFoundError("Account not found")

    return BalanceResponse(
        account_id=str(account.id),
        balance=account.balance,
        as_of_date=dt.datetime.now(dt.timezone.utc),
        currency=account.currency,
    )
