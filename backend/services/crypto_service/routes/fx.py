"""FX routes for crypto service (Frankfurter API proxy)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from crypto_service.market import fetch_latest_rates
from shared.redis import RedisClient

router = APIRouter(prefix="/api/v1/crypto", tags=["crypto"])
cache = RedisClient()


@router.get("/fx/latest")
def get_fx_latest(base: str = Query("EUR"), symbols: Optional[str] = Query(None)) -> dict:
    key = f"fx:latest:{base}:{symbols or ''}"
    cached = cache.get_json(key)
    if cached:
        return cached

    symbol_list = [s.strip().upper() for s in symbols.split(",")] if symbols else None
    data = fetch_latest_rates(base=base, symbols=symbol_list)
    cache.set_json(key, data, ttl_seconds=3600)
    return data
