# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Background task triggers for crypto service."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query, status

from crypto_service.workers import (
    evaluate_alerts,
    refresh_prices,
    sync_market_history,
    train_baseline_model,
)
from shared.exceptions import ValidationError

router = APIRouter(prefix="/api/v1/crypto/tasks", tags=["crypto-tasks"])


def _parse_symbols(symbols: Optional[str]) -> Optional[List[str]]:
    if symbols is None:
        return None
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if not symbol_list:
        raise ValidationError("At least one symbol is required")
    return symbol_list


@router.post("/refresh-prices", status_code=status.HTTP_202_ACCEPTED)
def enqueue_refresh_prices(
    symbols: Optional[str] = Query(default=None, description="Comma-separated symbols"),
    vs_currency: str = Query(default="usd"),
) -> dict:
    symbol_list = _parse_symbols(symbols)
    task = refresh_prices.delay(symbol_list, vs_currency)
    return {"task_id": task.id, "status": "queued"}


@router.post("/evaluate-alerts", status_code=status.HTTP_202_ACCEPTED)
def enqueue_evaluate_alerts() -> dict:
    task = evaluate_alerts.delay()
    return {"task_id": task.id, "status": "queued"}


@router.post("/sync-history", status_code=status.HTTP_202_ACCEPTED)
def enqueue_sync_history(
    symbol: Optional[str] = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
) -> dict:
    symbol_value = symbol.upper() if symbol else None
    task = sync_market_history.delay(symbol_value, days)
    return {"task_id": task.id, "status": "queued"}


@router.post("/train-model", status_code=status.HTTP_202_ACCEPTED)
def enqueue_train_model(
    model_name: str = Query(default="baseline-returns"),
    version: str = Query(default="baseline-returns-v1"),
) -> dict:
    task = train_baseline_model.delay(model_name, version)
    return {"task_id": task.id, "status": "queued"}
