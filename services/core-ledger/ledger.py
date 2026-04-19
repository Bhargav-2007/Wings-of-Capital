# Copyright 2026 Bhargav (Wings of Capital)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import EntryDirection, JournalEntry, LedgerPosting
from schemas import PostingRequest


def create_journal_entry(session: Session, payload: PostingRequest) -> dict:
    if not payload.lines:
        raise ValueError("Journal entry must include posting lines")

    currency = payload.lines[0].currency
    reference = payload.reference or f"JRNL-{uuid.uuid4().hex[:12].upper()}"

    entry = JournalEntry(reference=reference, currency=currency)
    session.add(entry)
    session.flush()

    debit_total = Decimal("0")
    credit_total = Decimal("0")

    for line in payload.lines:
        direction = EntryDirection.debit if line.direction == "debit" else EntryDirection.credit
        amount = Decimal(line.amount)

        if direction == EntryDirection.debit:
            debit_total += amount
        else:
            credit_total += amount

        session.add(
            LedgerPosting(
                entry_id=entry.id,
                account_id=line.account_id,
                direction=direction,
                amount=amount,
                currency=line.currency,
            )
        )

    if debit_total != credit_total:
        session.rollback()
        raise ValueError("Double-entry imbalance detected during persistence")

    session.commit()

    return {
        "entry_id": str(entry.id),
        "reference": entry.reference,
        "total_debits": debit_total,
        "total_credits": credit_total,
        "currency": currency,
        "line_count": len(payload.lines),
    }


def get_journal_entry_by_id(session: Session, entry_id: str) -> JournalEntry | None:
    return session.query(JournalEntry).filter(JournalEntry.id == entry_id).first()


def get_journal_entry_by_reference(session: Session, reference: str) -> JournalEntry | None:
    return session.query(JournalEntry).filter(JournalEntry.reference == reference).first()


def list_journal_entries(session: Session, limit: int) -> list[JournalEntry]:
    return session.query(JournalEntry).order_by(JournalEntry.created_at.desc()).limit(limit).all()


def get_account_balance(session: Session, account_id: str, currency: str) -> dict:
    debit_sum = (
        session.query(func.coalesce(func.sum(LedgerPosting.amount), 0))
        .filter(
            LedgerPosting.account_id == account_id,
            LedgerPosting.currency == currency,
            LedgerPosting.direction == EntryDirection.debit,
        )
        .scalar()
    )

    credit_sum = (
        session.query(func.coalesce(func.sum(LedgerPosting.amount), 0))
        .filter(
            LedgerPosting.account_id == account_id,
            LedgerPosting.currency == currency,
            LedgerPosting.direction == EntryDirection.credit,
        )
        .scalar()
    )

    debit_total = Decimal(str(debit_sum))
    credit_total = Decimal(str(credit_sum))

    return {
        "account_id": account_id,
        "currency": currency,
        "debits": debit_total,
        "credits": credit_total,
        "net_balance": debit_total - credit_total,
    }
