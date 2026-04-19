# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Price and portfolio routes for crypto service."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from crypto_service.dependencies import get_current_user_id
from crypto_service.market import fetch_prices
from crypto_service.models.holding import Holding
from crypto_service.models.market_price import MarketPrice
from crypto_service.schemas.portfolio import PortfolioHolding, PortfolioResponse
from crypto_service.schemas.prices import PriceQuote, PricesResponse
from shared.database import TimescaleSessionLocal, get_db
from shared.exceptions import ValidationError
from shared.redis import RedisClient

router = APIRouter(prefix="/api/v1/crypto", tags=["crypto"])
cache = RedisClient()


def _cache_key(symbols: List[str], currency: str) -> str:
    joined = ",".join(sorted(symbols))
    return f"crypto:prices:{currency}:{joined}"


def _store_market_prices(quotes: List[dict], currency: str) -> None:
    if TimescaleSessionLocal is None or currency.lower() != "usd":
        return
    session = TimescaleSessionLocal()
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


@router.get("/prices", response_model=PricesResponse)
def get_prices(
    symbols: str = Query(..., description="Comma-separated symbols"),
    vs_currency: str = Query(default="usd"),
) -> PricesResponse:
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if not symbol_list:
        raise ValidationError("At least one symbol is required")

    currency = vs_currency.lower()
    quotes = _get_price_quotes(symbol_list, currency)
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
    quotes = {quote.symbol: quote for quote in _get_price_quotes(symbols, "usd")}

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
