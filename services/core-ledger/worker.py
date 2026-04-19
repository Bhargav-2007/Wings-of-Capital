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

import os
from datetime import timedelta

from celery import Celery

from audit import append_audit_event, verify_audit_chain
from db import SessionLocal

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("core_ledger", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.task_default_queue = "ledger_tasks"
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.beat_schedule = {
    "audit-chain-verify-every-minute": {
        "task": "core_ledger.audit_verify_periodic",
        "schedule": timedelta(minutes=1),
    }
}


@celery_app.task(name="core_ledger.reconcile_entry")
def reconcile_entry(entry_id: str) -> dict:
    # Placeholder reconciliation hook for later invariant checks and settlement workflows.
    return {"entry_id": entry_id, "status": "queued-for-reconciliation"}


def trigger_reconciliation(entry_id: str) -> str | None:
    try:
        async_result = reconcile_entry.delay(entry_id)
        return async_result.id
    except Exception:
        # API should remain available even if the broker is temporarily unavailable.
        return None


@celery_app.task(name="core_ledger.audit_verify_periodic")
def audit_verify_periodic(limit: int = 5000) -> dict:
    session = SessionLocal()
    try:
        result = verify_audit_chain(session, limit=limit)
        if not result.get("valid", False):
            append_audit_event(
                session,
                event_type="ledger.audit.chain_invalid",
                entity_type="audit_chain",
                entity_id="global",
                payload={
                    "checked_events": result.get("checked_events", 0),
                    "issues_count": len(result.get("issues", [])),
                },
            )
        return result
    finally:
        session.close()
