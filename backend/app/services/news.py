"""Finnhub news access with a 15-minute cache.

One call per market scope at draw time; headlines are handed to the advice
layer (Gemini picks asset + event jointly; the fallback keyword-matches).
Any failure degrades to "no news" rather than failing the draw.
"""

import asyncio
import time
from dataclasses import dataclass

import httpx

from ..config import get_settings

BASE_URL = "https://finnhub.io/api/v1"
CACHE_TTL_SECONDS = 900  # news changes slowly; protect the 60 req/min budget
MAX_HEADLINES = 12


@dataclass
class NewsItem:
    headline: str
    url: str | None


_cache: dict[str, tuple[float, list[NewsItem]]] = {}
_locks: dict[str, asyncio.Lock] = {}


def _category(market: str) -> list[str]:
    if market == "stocks":
        return ["general"]
    if market == "crypto":
        return ["crypto"]
    return ["general", "crypto"]


async def recent_news(market: str) -> list[NewsItem]:
    """Recent headlines for the market scope, cached 15 min. Never raises."""
    now = time.monotonic()
    cached = _cache.get(market)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    key = get_settings().finnhub_api_key
    if not key:
        _cache[market] = (now, [])
        return []

    lock = _locks.get(market)
    if lock is None:
        lock = asyncio.Lock()
        _locks[market] = lock

    async with lock:
        now = time.monotonic()
        cached = _cache.get(market)
        if cached and now - cached[0] < CACHE_TTL_SECONDS:
            return cached[1]

        categories = _category(market)
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                for category in categories:
                    r = await client.get(
                        f"{BASE_URL}/news",
                        params={"category": category, "token": key},
                    )
                    if r.status_code != 200:
                        _cache[market] = (time.monotonic(), [])
                        return []
                    for article in r.json()[: MAX_HEADLINES // len(categories)]:
                        headline = (article.get("headline") or "").strip()
                        if headline:
                            items.append(NewsItem(headline=headline, url=article.get("url")))
        except Exception:
            _cache[market] = (time.monotonic(), [])
            return []  # news is flavor; a dead feed must never break a draw

        _cache[market] = (time.monotonic(), items)
        return items
