# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Price and portfolio routes for crypto service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from crypto_service.dependencies import get_current_user_id
from crypto_service.market import fetch_prices
from crypto_service.models.holding import Holding
from crypto_service.models.market_price import MarketPrice
from crypto_service.schemas.portfolio import PortfolioHolding, PortfolioResponse
from crypto_service.schemas.prices import PriceQuote, PricesResponse
from shared.config import get_settings
from shared.database import SessionLocal, TimescaleSessionLocal, get_db
from shared.exceptions import AppError, ValidationError
from shared.redis import RedisClient

router = APIRouter(prefix="/api/v1/crypto", tags=["crypto"])
cache = RedisClient()
settings = get_settings()


def _cache_key(symbols: List[str], currency: str) -> str:
    joined = ",".join(sorted(symbols))
    return f"crypto:prices:{currency}:{joined}"


def _store_market_prices(quotes: List[dict], currency: str) -> None:
    if TimescaleSessionLocal is None or currency.lower() != "usd":
        return

    session_factories = [TimescaleSessionLocal, SessionLocal]
    for factory in session_factories:
        if factory is None:
            continue
        session = factory()
        try:
            for quote in quotes:
                session.add(
                    MarketPrice(
                        symbol=quote["symbol"],
                        price_usd=Decimal(str(quote["price"])),
                        volume_24h=Decimal(str(quote["volume_24h"] or 0)),
                        market_cap=Decimal(str(quote["market_cap"] or 0)),
                        timestamp=quote["last_updated"],
                    )
                )
            session.commit()
            return
        except ProgrammingError:
            session.rollback()
        finally:
            session.close()


def _get_price_quotes(symbols: List[str], currency: str) -> List[PriceQuote]:
    key = _cache_key(symbols, currency)
    cached = cache.get_json(key)
    if cached:
        return [PriceQuote(**item) for item in cached]

    quotes = fetch_prices(symbols, currency)
    response = [
        PriceQuote(
            symbol=quote["symbol"],
            price=Decimal(str(quote["price"])),
            market_cap=Decimal(str(quote["market_cap"] or 0)),
            volume_24h=Decimal(str(quote["volume_24h"] or 0)),
            last_updated=quote["last_updated"],
        )
        for quote in quotes
    ]

    cache.set_json(key, [item.model_dump(mode="json") for item in response], ttl_seconds=60)
    _store_market_prices(quotes, currency)
    return response


def _fallback_quotes(symbols: List[str]) -> List[PriceQuote]:
    now = dt.datetime.now(dt.timezone.utc)
    return [
        PriceQuote(
            symbol=symbol,
            price=Decimal("0"),
            market_cap=Decimal("0"),
            volume_24h=Decimal("0"),
            last_updated=now,
        )
        for symbol in symbols
    ]


def _latest_quotes_from_db(symbols: List[str], currency: str) -> List[PriceQuote]:
    if currency.lower() != "usd":
        return _fallback_quotes(symbols)

    for factory in [TimescaleSessionLocal, SessionLocal]:
        if factory is None:
            continue
        session = factory()
        try:
            latest: dict[str, MarketPrice] = {}
            for symbol in symbols:
                row = (
                    session.execute(
                        select(MarketPrice)
                        .where(MarketPrice.symbol == symbol)
                        .order_by(MarketPrice.timestamp.desc())
                        .limit(1)
                    )
                    .scalars()
                    .first()
                )
                if row:
                    latest[symbol] = row

            if not latest:
                continue

            return [
                PriceQuote(
                    symbol=symbol,
                    price=Decimal(str(latest[symbol].price_usd)) if symbol in latest else Decimal("0"),
                    market_cap=Decimal(str(latest[symbol].market_cap)) if symbol in latest else Decimal("0"),
                    volume_24h=Decimal(str(latest[symbol].volume_24h)) if symbol in latest else Decimal("0"),
                    last_updated=latest[symbol].timestamp if symbol in latest else dt.datetime.now(dt.timezone.utc),
                )
                for symbol in symbols
            ]
        except ProgrammingError:
            continue
        finally:
            session.close()

    return _fallback_quotes(symbols)


def get_price_quotes(symbols: List[str], currency: str) -> List[PriceQuote]:
    try:
        return _get_price_quotes(symbols, currency)
    except ValidationError:
        raise
    except Exception as exc:
        if settings.environment.lower() in {"development", "dev", "local"}:
            return _latest_quotes_from_db(symbols, currency)
        raise AppError(
            "Market data unavailable",
            status_code=502,
            details={"error": str(exc)},
        )


@router.get("/prices", response_model=PricesResponse)
def get_prices(
    symbols: str = Query(..., description="Comma-separated symbols"),
    vs_currency: str = Query(default="usd"),
) -> PricesResponse:
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if not symbol_list:
        raise ValidationError("At least one symbol is required")

    currency = vs_currency.lower()
    quotes = get_price_quotes(symbol_list, currency)
    return PricesResponse(currency=currency, data=quotes)


@router.get("/portfolio", response_model=PortfolioResponse)
def get_portfolio(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PortfolioResponse:
    holdings = db.execute(select(Holding).where(Holding.user_id == user_id)).scalars().all()

    if not holdings:
        return PortfolioResponse(
            total_value=Decimal("0"),
            total_cost=Decimal("0"),
            total_pnl=Decimal("0"),
            allocation={},
            holdings=[],
        )

    symbols = [holding.symbol.upper() for holding in holdings]
    quotes = {quote.symbol: quote for quote in get_price_quotes(symbols, "usd")}

    portfolio_holdings = []
    total_value = Decimal("0")
    total_cost = Decimal("0")

    for holding in holdings:
        quote = quotes.get(holding.symbol.upper())
        if not quote:
            continue

        current_value = Decimal(holding.quantity) * Decimal(quote.price)
        cost = Decimal(holding.cost_basis)
        pnl = current_value - cost
        pnl_percent = (pnl / cost * Decimal("100")) if cost > 0 else Decimal("0")

        portfolio_holdings.append(
            PortfolioHolding(
                symbol=holding.symbol.upper(),
                quantity=holding.quantity,
                cost_basis=cost,
                current_price=quote.price,
                current_value=current_value,
                pnl=pnl,
                pnl_percent=pnl_percent,
            )
        )

        total_value += current_value
        total_cost += cost

    total_pnl = total_value - total_cost
    allocation = {
        holding.symbol: (holding.current_value / total_value * Decimal("100")) if total_value > 0 else Decimal("0")
        for holding in portfolio_holdings
    }

    return PortfolioResponse(
        total_value=total_value,
        total_cost=total_cost,
        total_pnl=total_pnl,
        allocation=allocation,
        holdings=portfolio_holdings,
    )
