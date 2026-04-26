"""Frankfurter FX client (no API key required).

Simple wrapper used by the crypto/market layer to fetch latest FX rates.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import requests

_BASE_URL = "https://api.frankfurter.app"


def fetch_latest_rates(base: str = "EUR", symbols: Optional[List[str]] = None) -> Dict:
    params: Dict[str, str] = {}
    if base:
        params["from"] = base.upper()
    if symbols:
        params["to"] = ",".join([s.upper() for s in symbols])

    resp = requests.get(f"{_BASE_URL}/latest", params=params, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    return {
        "base": payload.get("base"),
        "date": payload.get("date"),
        "rates": payload.get("rates", {}),
    }
