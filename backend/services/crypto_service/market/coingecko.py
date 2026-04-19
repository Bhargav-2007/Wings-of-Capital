# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""CoinGecko API client."""

from __future__ import annotations

import datetime as dt
from typing import Dict, List

import requests

from shared.config import get_settings
from shared.exceptions import ValidationError

_BASE_URL = "https://api.coingecko.com/api/v3"

_SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "USDC": "usd-coin",
    "BNB": "binancecoin",
    "SOL": "solana",
    "ADA": "cardano",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "MATIC": "matic-network",
    "DOT": "polkadot",
    "LTC": "litecoin",
    "LINK": "chainlink",
}


def _headers() -> Dict[str, str]:
    settings = get_settings()
    headers = {"Accept": "application/json"}
    if settings.coingecko_api_key:
        headers["x-cg-demo-api-key"] = settings.coingecko_api_key
    return headers


def _resolve_ids(symbols: List[str]) -> Dict[str, str]:
    resolved = {}
    for symbol in symbols:
        upper = symbol.upper()
        if upper not in _SYMBOL_MAP:
            raise ValidationError(f"Unsupported symbol: {symbol}")
        resolved[upper] = _SYMBOL_MAP[upper]
    return resolved


def fetch_prices(symbols: List[str], vs_currency: str = "usd") -> List[dict]:
    resolved = _resolve_ids(symbols)
    ids = ",".join(resolved.values())

    response = requests.get(
        f"{_BASE_URL}/simple/price",
        params={
            "ids": ids,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_last_updated_at": "true",
        },
        headers=_headers(),
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    quotes = []
    for symbol, coin_id in resolved.items():
        data = payload.get(coin_id)
        if not data:
            raise ValidationError(f"No price data for {symbol}")

        updated_at = dt.datetime.fromtimestamp(data.get("last_updated_at", 0), tz=dt.timezone.utc)
        quotes.append(
            {
                "symbol": symbol,
                "price": data.get(vs_currency),
                "market_cap": data.get(f"{vs_currency}_market_cap"),
                "volume_24h": data.get(f"{vs_currency}_24h_vol"),
                "last_updated": updated_at,
            }
        )

    return quotes


def fetch_market_chart(symbol: str, days: int = 30, vs_currency: str = "usd") -> List[dict]:
    resolved = _resolve_ids([symbol])
    coin_id = resolved[symbol.upper()]

    response = requests.get(
        f"{_BASE_URL}/coins/{coin_id}/market_chart",
        params={"vs_currency": vs_currency, "days": days},
        headers=_headers(),
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    prices = payload.get("prices", [])
    market_caps = payload.get("market_caps", [])
    volumes = payload.get("total_volumes", [])

    market_cap_map = {int(item[0]): item[1] for item in market_caps}
    volume_map = {int(item[0]): item[1] for item in volumes}

    series = []
    for ts_ms, price in prices:
        timestamp = dt.datetime.fromtimestamp(ts_ms / 1000.0, tz=dt.timezone.utc)
        series.append(
            {
                "timestamp": timestamp,
                "price": price,
                "market_cap": market_cap_map.get(int(ts_ms), 0),
                "volume_24h": volume_map.get(int(ts_ms), 0),
            }
        )

    return series
