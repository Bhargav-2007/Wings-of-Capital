# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""AI prediction routes for crypto service."""

from __future__ import annotations

import datetime as dt
import math
import statistics
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from crypto_service.dependencies import get_current_user_id
from crypto_service.market import fetch_market_chart
from crypto_service.models.market_price import MarketPrice
from crypto_service.schemas.predictions import PredictionRequest, PredictionResponse
from shared.database import TimescaleSessionLocal, get_db
from shared.exceptions import ValidationError

router = APIRouter(prefix="/api/v1/crypto/ai", tags=["crypto-ai"])

_MODEL_VERSION = "baseline-returns-v1"


def _store_history(db: Session, symbol: str, series: list[dict]) -> None:
    sessions: list[Session] = []
    if TimescaleSessionLocal is not None:
        sessions.append(TimescaleSessionLocal())
    sessions.append(db)

    for session in sessions:
        try:
            existing_ts = session.execute(
                select(MarketPrice.timestamp).where(MarketPrice.symbol == symbol)
            ).scalars().all()
            existing_set = {ts for ts in existing_ts}

            for item in series:
                if item["timestamp"] in existing_set:
                    continue
                session.add(
                    MarketPrice(
                        symbol=symbol,
                        price_usd=Decimal(str(item["price"])),
                        volume_24h=Decimal(str(item["volume_24h"] or 0)),
                        market_cap=Decimal(str(item["market_cap"] or 0)),
                        timestamp=item["timestamp"],
                    )
                )
            session.commit()
        finally:
            if session is not db:
                session.close()


def _load_prices(db: Session, symbol: str, limit: int = 90) -> list[MarketPrice]:
    session = TimescaleSessionLocal() if TimescaleSessionLocal is not None else db
    try:
        return (
            session.execute(
                select(MarketPrice)
                .where(MarketPrice.symbol == symbol)
                .order_by(MarketPrice.timestamp.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
    finally:
        if session is not db:
            session.close()


def _calculate_forecast(prices: list[MarketPrice], horizon_days: int) -> tuple[Decimal, list[Decimal]]:
    series = [float(item.price_usd) for item in reversed(prices)]
    if len(series) < 5:
        raise ValidationError("Insufficient price history for prediction")

    returns = []
    for idx in range(1, len(series)):
        prev = series[idx - 1]
        current = series[idx]
        if prev <= 0:
            continue
        returns.append((current - prev) / prev)

    if len(returns) < 2:
        raise ValidationError("Insufficient price history for prediction")

    mean_return = statistics.mean(returns)
    volatility = statistics.pstdev(returns)

    expected_return = mean_return * horizon_days
    sigma = volatility * math.sqrt(horizon_days)

    last_price = series[-1]
    forecast = last_price * (1 + expected_return)
    lower = last_price * (1 + expected_return - 1.96 * sigma)
    upper = last_price * (1 + expected_return + 1.96 * sigma)

    forecast = max(forecast, 0)
    lower = max(lower, 0)
    upper = max(upper, 0)

    return Decimal(str(forecast)), [Decimal(str(lower)), Decimal(str(upper))]


@router.post("/predictions", response_model=PredictionResponse)
def predict_price(
    payload: PredictionRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    symbol = payload.symbol.upper()

    prices = _load_prices(db, symbol, limit=90)
    if len(prices) < 30:
        series = fetch_market_chart(symbol, days=90)
        _store_history(db, symbol, series)
        prices = _load_prices(db, symbol, limit=90)

    forecast, interval = _calculate_forecast(prices, payload.horizon_days)

    return PredictionResponse(
        symbol=symbol,
        horizon_days=payload.horizon_days,
        forecast=forecast,
        confidence_interval=interval,
        model_version=_MODEL_VERSION,
    )
