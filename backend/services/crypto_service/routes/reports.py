# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Reporting endpoints for crypto portfolios."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Dict, Iterable, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from crypto_service.dependencies import get_current_user_id
from crypto_service.models.holding import Holding
from crypto_service.models.market_price import MarketPrice
from crypto_service.routes.prices import get_price_quotes
from crypto_service.schemas.reports import (
    AllocationHistoryResponse,
    AllocationPoint,
    PnlHistoryPoint,
    PnlHistoryResponse,
    PnlPosition,
    PnlSummary,
)
from shared.database import TimescaleSessionLocal, get_db

router = APIRouter(prefix="/api/v1/crypto/reports", tags=["crypto-reports"])


def _date_range(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    current = start
    while current <= end:
        yield current
        current += dt.timedelta(days=1)


def _load_holdings(db: Session, user_id: str) -> List[Holding]:
    return db.execute(select(Holding).where(Holding.user_id == user_id)).scalars().all()


def _load_market_prices(symbols: List[str], start_dt: dt.datetime, db: Session) -> List[MarketPrice]:
    session_factories = [TimescaleSessionLocal, None]
    for factory in session_factories:
        session = db if factory is None else factory()
        try:
            return (
                session.execute(
                    select(MarketPrice)
                    .where(MarketPrice.symbol.in_(symbols), MarketPrice.timestamp >= start_dt)
                    .order_by(MarketPrice.timestamp.asc())
                )
                .scalars()
                .all()
            )
        except ProgrammingError:
            continue
        finally:
            if session is not db:
                session.close()
    return []


def _build_daily_price_updates(rows: List[MarketPrice]) -> Dict[dt.date, Dict[str, Decimal]]:
    updates: Dict[dt.date, Dict[str, Decimal]] = {}
    for row in rows:
        day = row.timestamp.date()
        updates.setdefault(day, {})[row.symbol.upper()] = Decimal(row.price_usd)
    return updates


@router.get("/pnl-summary", response_model=PnlSummary)
def pnl_summary(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PnlSummary:
    holdings = _load_holdings(db, user_id)
    if not holdings:
        return PnlSummary(
            total_value=Decimal("0"),
            total_cost=Decimal("0"),
            total_pnl=Decimal("0"),
            pnl_percent=Decimal("0"),
            positions=[],
        )

    symbols = [holding.symbol.upper() for holding in holdings]
    quotes = {quote.symbol: quote for quote in get_price_quotes(symbols, "usd")}

    total_value = Decimal("0")
    total_cost = Decimal("0")
    positions: List[PnlPosition] = []

    for holding in holdings:
        quote = quotes.get(holding.symbol.upper())
        if not quote:
            continue
        current_value = Decimal(holding.quantity) * Decimal(quote.price)
        cost = Decimal(holding.cost_basis)
        pnl = current_value - cost
        pnl_percent = (pnl / cost * Decimal("100")) if cost > 0 else Decimal("0")

        positions.append(
            PnlPosition(
                symbol=holding.symbol.upper(),
                quantity=holding.quantity,
                cost_basis=cost,
                current_price=Decimal(quote.price),
                current_value=current_value,
                pnl=pnl,
                pnl_percent=pnl_percent,
            )
        )

        total_value += current_value
        total_cost += cost

    total_pnl = total_value - total_cost
    total_pnl_percent = (total_pnl / total_cost * Decimal("100")) if total_cost > 0 else Decimal("0")

    return PnlSummary(
        total_value=total_value,
        total_cost=total_cost,
        total_pnl=total_pnl,
        pnl_percent=total_pnl_percent,
        positions=positions,
    )


@router.get("/pnl-history", response_model=PnlHistoryResponse)
def pnl_history(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=7, le=365),
) -> PnlHistoryResponse:
    holdings = _load_holdings(db, user_id)
    if not holdings:
        return PnlHistoryResponse(currency="usd", points=[])

    symbols = [holding.symbol.upper() for holding in holdings]
    end_dt = dt.datetime.now(dt.timezone.utc)
    start_dt = end_dt - dt.timedelta(days=days)

    rows = _load_market_prices(symbols, start_dt, db)
    updates = _build_daily_price_updates(rows)

    quantity_map = {holding.symbol.upper(): Decimal(holding.quantity) for holding in holdings}
    cost_total = sum(Decimal(holding.cost_basis) for holding in holdings)

    latest_prices: Dict[str, Decimal] = {symbol: Decimal("0") for symbol in symbols}
    points: List[PnlHistoryPoint] = []

    for day in _date_range(start_dt.date(), end_dt.date()):
        if day in updates:
            for symbol, price in updates[day].items():
                latest_prices[symbol] = price

        total_value = sum(latest_prices[symbol] * quantity_map[symbol] for symbol in symbols)
        total_pnl = total_value - cost_total
        pnl_percent = (total_pnl / cost_total * Decimal("100")) if cost_total > 0 else Decimal("0")

        points.append(
            PnlHistoryPoint(
                date=day,
                total_value=total_value,
                total_cost=cost_total,
                total_pnl=total_pnl,
                pnl_percent=pnl_percent,
            )
        )

    return PnlHistoryResponse(currency="usd", points=points)


@router.get("/allocation-history", response_model=AllocationHistoryResponse)
def allocation_history(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=7, le=365),
) -> AllocationHistoryResponse:
    holdings = _load_holdings(db, user_id)
    if not holdings:
        return AllocationHistoryResponse(currency="usd", points=[])

    symbols = [holding.symbol.upper() for holding in holdings]
    end_dt = dt.datetime.now(dt.timezone.utc)
    start_dt = end_dt - dt.timedelta(days=days)

    rows = _load_market_prices(symbols, start_dt, db)
    updates = _build_daily_price_updates(rows)

    quantity_map = {holding.symbol.upper(): Decimal(holding.quantity) for holding in holdings}
    latest_prices: Dict[str, Decimal] = {symbol: Decimal("0") for symbol in symbols}
    points: List[AllocationPoint] = []

    for day in _date_range(start_dt.date(), end_dt.date()):
        if day in updates:
            for symbol, price in updates[day].items():
                latest_prices[symbol] = price

        total_value = sum(latest_prices[symbol] * quantity_map[symbol] for symbol in symbols)
        allocation = {
            symbol: (latest_prices[symbol] * quantity_map[symbol] / total_value * Decimal("100"))
            if total_value > 0
            else Decimal("0")
            for symbol in symbols
        }

        points.append(
            AllocationPoint(
                date=day,
                total_value=total_value,
                allocation=allocation,
            )
        )

    return AllocationHistoryResponse(currency="usd", points=points)
