"""Finnhub quote access with a short in-memory cache (ADR-0001).

One module owns the provider; swapping Finnhub for another source is a
local change. Free tier is 60 calls/minute — the 60s cache keeps us safe.
"""

import time
from decimal import Decimal

import httpx
from fastapi import HTTPException

from ..config import get_settings

BASE_URL = "https://finnhub.io/api/v1"
CACHE_TTL_SECONDS = 60

_cache: dict[str, tuple[float, Decimal]] = {}


async def current_price(symbol: str) -> Decimal:
    """Latest trade price for a symbol. Cached for 60s per symbol."""
    now = time.monotonic()
    if symbol in _cache:
        cached_at, price = _cache[symbol]
        if now - cached_at < CACHE_TTL_SECONDS:
            return price

    key = get_settings().finnhub_api_key
    if not key:
        raise HTTPException(status_code=503, detail="Price feed not configured (FINNHUB key missing)")

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{BASE_URL}/quote",
            params={"symbol": symbol, "token": key},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Price feed error")
    payload = r.json()
    price = payload.get("c")  # current price
    if not price:
        raise HTTPException(status_code=404, detail=f"No quote for {symbol}")

    value = Decimal(str(price))
    _cache[symbol] = (now, value)
    return value


async def prices_for(symbols: list[str]) -> dict[str, Decimal | None]:
    """Fetch several symbols, reusing the cache. A failing symbol maps to
    None so one bad quote can't take down the whole positions view."""
    out: dict[str, Decimal | None] = {}
    for symbol in dict.fromkeys(symbols):
        try:
            out[symbol] = await current_price(symbol)
        except HTTPException:
            out[symbol] = None
    return out
