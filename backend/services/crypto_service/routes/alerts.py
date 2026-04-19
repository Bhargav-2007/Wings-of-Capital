# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Price alert routes for crypto service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from crypto_service.dependencies import get_current_user_id
from crypto_service.market import fetch_prices
from crypto_service.models.enums import PriceAlertCondition
from crypto_service.models.price_alert import PriceAlert
from crypto_service.schemas.alerts import PriceAlertCreate, PriceAlertOut
from shared.database import get_db
from shared.exceptions import ValidationError

router = APIRouter(prefix="/api/v1/crypto/alerts", tags=["crypto-alerts"])


def _should_trigger(condition: PriceAlertCondition, price: Decimal, target: Decimal) -> bool:
    if condition == PriceAlertCondition.ABOVE:
        return price >= target
    return price <= target


@router.post("", response_model=PriceAlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: PriceAlertCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PriceAlertOut:
    symbol = payload.symbol.upper()

    current_price = None
    try:
        quotes = fetch_prices([symbol])
        current_price = Decimal(str(quotes[0]["price"]))
    except ValidationError:
        raise
    except Exception:
        current_price = None

    triggered_at = None
    if current_price is not None and _should_trigger(payload.condition, current_price, payload.target_price):
        triggered_at = dt.datetime.now(dt.timezone.utc)

    alert = PriceAlert(
        user_id=user_id,
        symbol=symbol,
        target_price=payload.target_price,
        condition=payload.condition,
        enabled=True,
        triggered_at=triggered_at,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return PriceAlertOut(
        id=str(alert.id),
        symbol=alert.symbol,
        target_price=alert.target_price,
        condition=alert.condition,
        enabled=alert.enabled,
        triggered_at=alert.triggered_at,
        created_at=alert.created_at,
    )


@router.get("", response_model=list[PriceAlertOut])
def list_alerts(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> list[PriceAlertOut]:
    alerts = db.execute(select(PriceAlert).where(PriceAlert.user_id == user_id)).scalars().all()
    return [
        PriceAlertOut(
            id=str(alert.id),
            symbol=alert.symbol,
            target_price=alert.target_price,
            condition=alert.condition,
            enabled=alert.enabled,
            triggered_at=alert.triggered_at,
            created_at=alert.created_at,
        )
        for alert in alerts
    ]
