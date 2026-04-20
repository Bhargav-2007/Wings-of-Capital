#!/usr/bin/env python3
# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Seed crypto holdings and market prices for development."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError

ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "backend" / "services"
sys.path.insert(0, str(SERVICES_DIR))

os.environ.setdefault("DATABASE_URL", "postgresql://woc_user:woc_password@localhost:5432/wings_of_capital")
os.environ.setdefault("TIMESCALE_URL", "postgresql://woc_user:woc_password@localhost:5433/wings_timescale")
os.environ.setdefault("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

from shared.database import SessionLocal, TimescaleSessionLocal  # noqa: E402
from crypto_service.models.holding import Holding  # noqa: E402
from crypto_service.models.market_price import MarketPrice  # noqa: E402


BASE_PRICES = {
    "BTC": Decimal("60000"),
    "ETH": Decimal("3000"),
    "SOL": Decimal("150"),
    "USDT": Decimal("1"),
}
DEFAULT_QUANTITIES = {
    "BTC": Decimal("0.5"),
    "ETH": Decimal("5"),
    "SOL": Decimal("100"),
    "USDT": Decimal("1000"),
}


def _parse_symbols(value: str) -> list[str]:
    return [symbol.strip().upper() for symbol in value.split(",") if symbol.strip()]


def _iter_days(start: dt.datetime, days: int) -> Iterable[dt.datetime]:
    for offset in range(days):
        yield start + dt.timedelta(days=offset)


def _seed_holdings(session, user_id: str, symbols: list[str]) -> int:
    existing = session.execute(
        select(Holding.symbol).where(Holding.user_id == user_id)
    ).scalars().all()
    existing_set = {symbol.upper() for symbol in existing}

    inserted = 0
    now = dt.datetime.now(dt.timezone.utc)

    for symbol in symbols:
        if symbol in existing_set:
            continue
        quantity = DEFAULT_QUANTITIES.get(symbol, Decimal("1"))
        base_price = BASE_PRICES.get(symbol, Decimal("100"))
        cost_basis = (base_price * quantity * Decimal("0.9")).quantize(Decimal("0.000000000001"))

        session.add(
            Holding(
                user_id=user_id,
                symbol=symbol,
                quantity=quantity,
                cost_basis=cost_basis,
                acquired_at=now,
            )
        )
        inserted += 1

    session.commit()
    return inserted


def _seed_market_prices(session, symbols: list[str], days: int) -> int:
    inserted = 0
    end = dt.datetime.now(dt.timezone.utc)
    start = end - dt.timedelta(days=days - 1)

    for symbol in symbols:
        existing_ts = session.execute(
            select(MarketPrice.timestamp)
            .where(MarketPrice.symbol == symbol, MarketPrice.timestamp >= start)
        ).scalars().all()
        existing_set = {ts.date() for ts in existing_ts}

        base_price = BASE_PRICES.get(symbol, Decimal("100"))
        trend_step = Decimal("0.05") / Decimal(max(days - 1, 1))

        for idx, timestamp in enumerate(_iter_days(start, days)):
            if timestamp.date() in existing_set:
                continue
            multiplier = Decimal("1") + trend_step * Decimal(idx)
            price = (base_price * multiplier).quantize(Decimal("0.000000000001"))
            market_cap = (price * Decimal("1000000")).quantize(Decimal("0.000000000001"))
            volume = (price * Decimal("10000")).quantize(Decimal("0.000000000001"))

            session.add(
                MarketPrice(
                    symbol=symbol,
                    price_usd=price,
                    volume_24h=volume,
                    market_cap=market_cap,
                    timestamp=timestamp,
                )
            )
            inserted += 1

    session.commit()
    return inserted


def _run_price_seed(symbols: list[str], days: int) -> dict:
    inserted = 0
    for factory in [TimescaleSessionLocal, SessionLocal]:
        if factory is None:
            continue
        session = factory()
        try:
            inserted += _seed_market_prices(session, symbols, days)
        except ProgrammingError:
            session.rollback()
        finally:
            session.close()
    return {"prices_inserted": inserted}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed crypto holdings and market prices")
    parser.add_argument("--user-id", default=None, help="User id for holdings")
    parser.add_argument("--symbols", default="BTC,ETH,SOL,USDT", help="Comma-separated symbols")
    parser.add_argument("--days", type=int, default=30, help="Days of price history")
    parser.add_argument("--skip-holdings", action="store_true", help="Skip holdings seed")
    parser.add_argument("--skip-prices", action="store_true", help="Skip price history seed")
    args = parser.parse_args()

    user_id = args.user_id or str(uuid.uuid4())
    symbols = _parse_symbols(args.symbols)

    results = {"user_id": user_id, "symbols": symbols, "holdings_inserted": 0, "prices_inserted": 0}

    if not args.skip_holdings:
        session = SessionLocal()
        try:
            results["holdings_inserted"] = _seed_holdings(session, user_id, symbols)
        finally:
            session.close()

    if not args.skip_prices:
        results.update(_run_price_seed(symbols, args.days))

    print("Seed complete:")
    print(results)


if __name__ == "__main__":
    main()
