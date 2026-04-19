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
from ledger import create_journal_entry
from schemas import PostingRequest, PostingResponse
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
