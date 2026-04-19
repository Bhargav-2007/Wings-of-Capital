# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Transaction routes for ledger service."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ledger_service.dependencies import get_current_user_id
from ledger_service.ledger.posting import post_transaction
from ledger_service.models.transaction import Transaction
from ledger_service.models.transaction_line import TransactionLine
from ledger_service.schemas.transactions import TransactionCreate, TransactionLineOut, TransactionOut
from shared.database import get_db
from shared.schemas import PaginatedResponse

router = APIRouter(prefix="/api/v1/ledger/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> TransactionOut:
    transaction = post_transaction(db, payload, user_id)

    lines = db.execute(
        select(TransactionLine).where(TransactionLine.transaction_id == transaction.id)
    ).scalars().all()

    return TransactionOut(
        id=str(transaction.id),
        description=transaction.description,
        reference=transaction.reference,
        transaction_date=transaction.transaction_date,
        posted_at=transaction.posted_at,
        created_by=str(transaction.created_by),
        lines=[TransactionLineOut.model_validate(line) for line in lines],
    )


@router.get("", response_model=PaginatedResponse[TransactionOut])
def list_transactions(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    account_id: Optional[str] = None,
    date_from: Optional[dt.date] = None,
    date_to: Optional[dt.date] = None,
) -> PaginatedResponse[TransactionOut]:
    query = select(Transaction).where(Transaction.created_by == user_id)

    if date_from:
        query = query.where(Transaction.transaction_date >= dt.datetime.combine(date_from, dt.time.min, tzinfo=dt.timezone.utc))
    if date_to:
        query = query.where(Transaction.transaction_date <= dt.datetime.combine(date_to, dt.time.max, tzinfo=dt.timezone.utc))
    if account_id:
        query = query.join(TransactionLine).where(TransactionLine.account_id == account_id).distinct()

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

    transactions = db.execute(query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit)).scalars().all()
    txn_ids = [txn.id for txn in transactions]

    lines_map = {}
    if txn_ids:
        lines = db.execute(select(TransactionLine).where(TransactionLine.transaction_id.in_(txn_ids))).scalars().all()
        for line in lines:
            lines_map.setdefault(str(line.transaction_id), []).append(TransactionLineOut.model_validate(line))

    items = [
        TransactionOut(
            id=str(txn.id),
            description=txn.description,
            reference=txn.reference,
            transaction_date=txn.transaction_date,
            posted_at=txn.posted_at,
            created_by=str(txn.created_by),
            lines=lines_map.get(str(txn.id), []),
        )
        for txn in transactions
    ]

    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)
