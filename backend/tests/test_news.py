import asyncio

from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.anyio


class Response:
    status_code = 200

    def json(self):
        return [{"headline": "Alpha announces results", "url": "https://news.example/a"}]


class FakeAsyncClient:
    def __init__(self, *, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, url, params):
        CALLS.append(params["category"])
        return Response()


CALLS = []


async def test_news_uses_market_categories_and_caches_for_15_minutes(monkeypatch):
    from app.services import news

    monkeypatch.setattr(news, "_cache", {})
    monkeypatch.setattr(news, "httpx", SimpleNamespace(AsyncClient=FakeAsyncClient))
    monkeypatch.setattr(
        news, "get_settings", lambda: SimpleNamespace(finnhub_api_key="test-key")
    )
    CALLS.clear()
    now = [100.0]
    monkeypatch.setattr(news.time, "monotonic", lambda: now[0])
    stocks = await news.recent_news("stocks")
    assert [item.headline for item in stocks] == ["Alpha announces results"]
    assert CALLS == ["general"]

    cached = await news.recent_news("stocks")
    assert [item.url for item in cached] == ["https://news.example/a"]
    assert CALLS == ["general"]

    await news.recent_news("crypto")
    assert CALLS == ["general", "crypto"]

    now[0] += news.CACHE_TTL_SECONDS
    await news.recent_news("stocks")
    assert CALLS == ["general", "crypto", "general"]


async def test_news_provider_failure_degrades_and_is_cached(monkeypatch):
    from app.services import news

    class FailingClient(FakeAsyncClient):
        async def get(self, url, params):
            CALLS.append(params["category"])
            raise OSError("Finnhub unavailable")

    monkeypatch.setattr(news, "_cache", {})
    monkeypatch.setattr(news, "httpx", SimpleNamespace(AsyncClient=FailingClient))
    monkeypatch.setattr(
        news, "get_settings", lambda: SimpleNamespace(finnhub_api_key="test-key")
    )
    CALLS.clear()

    assert await news.recent_news("stocks") == []
    assert await news.recent_news("stocks") == []
    assert CALLS == ["general"]

async def test_any_failed_category_degrades_scope_to_empty_and_is_cached(monkeypatch):
    from app.services import news

    class PartialFailureClient(FakeAsyncClient):
        async def get(self, url, params):
            category = params["category"]
            CALLS.append(category)
            if category == "crypto":
                return SimpleNamespace(status_code=503)
            return Response()

    monkeypatch.setattr(news, "_cache", {})
    monkeypatch.setattr(news, "httpx", SimpleNamespace(AsyncClient=PartialFailureClient))
    monkeypatch.setattr(
        news, "get_settings", lambda: SimpleNamespace(finnhub_api_key="test-key")
    )
    CALLS.clear()

    assert await news.recent_news("all") == []
    assert CALLS == ["general", "crypto"]

    assert await news.recent_news("all") == []
    assert CALLS == ["general", "crypto"]

async def test_concurrent_cache_misses_fetch_once(monkeypatch):
    from app.services import news

    entered_fetch = asyncio.Event()
    release_fetch = asyncio.Event()

    class SlowClient(FakeAsyncClient):
        async def get(self, url, params):
            CALLS.append(params["category"])
            entered_fetch.set()
            await release_fetch.wait()
            return Response()

    monkeypatch.setattr(news, "_cache", {})
    monkeypatch.setattr(news, "httpx", SimpleNamespace(AsyncClient=SlowClient))
    monkeypatch.setattr(
        news, "get_settings", lambda: SimpleNamespace(finnhub_api_key="test-key")
    )
    CALLS.clear()

    first = asyncio.create_task(news.recent_news("stocks"))
    await entered_fetch.wait()
    second = asyncio.create_task(news.recent_news("stocks"))
    await asyncio.sleep(0)
    release_fetch.set()
    first_items, second_items = await asyncio.gather(first, second)

    assert first_items == second_items
    assert CALLS == ["general"]
