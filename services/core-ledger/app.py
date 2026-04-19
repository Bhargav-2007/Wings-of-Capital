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

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db import Base, engine, get_db_session
from ledger import (
    create_journal_entry,
    get_account_balance,
    get_journal_entry_by_id,
    get_journal_entry_by_reference,
    list_journal_entries,
)
from schemas import (
    AccountBalanceResponse,
    JournalEntryResponse,
    JournalListResponse,
    LedgerLineResponse,
    PostingRequest,
    PostingResponse,
)
from worker import trigger_reconciliation

app = FastAPI(title="Wings of Capital - Core Ledger")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"service": "core-ledger", "status": "ok"}


@app.post("/ledger/posting", response_model=PostingResponse)
def post_ledger_entry(payload: PostingRequest, db: Session = Depends(get_db_session)) -> PostingResponse:
    try:
        result = create_journal_entry(db, payload)
        task_id = trigger_reconciliation(result["entry_id"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to create ledger entry") from exc

    return PostingResponse(
        accepted=True,
        entry_id=result["entry_id"],
        reference=result["reference"],
        total_debits=result["total_debits"],
        total_credits=result["total_credits"],
        currency=result["currency"],
        line_count=result["line_count"],
        reconciliation_task_id=task_id,
    )


def _to_journal_response(entry) -> JournalEntryResponse:
    return JournalEntryResponse(
        entry_id=str(entry.id),
        reference=entry.reference,
        currency=entry.currency,
        created_at=entry.created_at.isoformat() if entry.created_at else "",
        lines=[
            LedgerLineResponse(
                account_id=line.account_id,
                direction=line.direction.value,
                amount=line.amount,
                currency=line.currency,
            )
            for line in entry.postings
        ],
    )


@app.get("/ledger/entry/{entry_id}", response_model=JournalEntryResponse)
def get_ledger_entry(entry_id: str, db: Session = Depends(get_db_session)) -> JournalEntryResponse:
    entry = get_journal_entry_by_id(db, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return _to_journal_response(entry)


@app.get("/ledger/reference/{reference}", response_model=JournalEntryResponse)
def get_ledger_entry_by_reference(reference: str, db: Session = Depends(get_db_session)) -> JournalEntryResponse:
    entry = get_journal_entry_by_reference(db, reference)
    if entry is None:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return _to_journal_response(entry)


@app.get("/ledger/journals", response_model=JournalListResponse)
def get_ledger_journals(limit: int = 50, db: Session = Depends(get_db_session)) -> JournalListResponse:
    bounded_limit = max(1, min(limit, 200))
    entries = list_journal_entries(db, bounded_limit)
    items = [_to_journal_response(entry) for entry in entries]
    return JournalListResponse(items=items, count=len(items))


@app.get("/ledger/account/{account_id}/balance", response_model=AccountBalanceResponse)
def get_ledger_account_balance(account_id: str, currency: str, db: Session = Depends(get_db_session)) -> AccountBalanceResponse:
    balance = get_account_balance(db, account_id=account_id, currency=currency.upper())
    return AccountBalanceResponse(**balance)
