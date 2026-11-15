import pytest

pytestmark = pytest.mark.anyio

USER = {"email": "reader@example.com", "name": "Reader", "password": "supersecret1"}


async def test_health(client):
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_readings_require_auth(client):
    r = await client.post("/api/readings", json={"question": "Will we ship on time?"})
    assert r.status_code == 401


async def test_create_and_get_reading(client):
    await client.post("/api/auth/register", json=USER)

    r = await client.post("/api/readings", json={})
    assert r.status_code == 201
    body = r.json()
    assert body["question"] == "What do the cards advise?"
    assert len(body["cards"]) == 3
    assert {c["position"] for c in body["cards"]} == {"past", "present", "future"}

    r2 = await client.get(f"/api/readings/{body['id']}")
    assert r2.status_code == 200
    assert r2.json()["id"] == body["id"]


async def test_get_reading_404(client):
    await client.post("/api/auth/register", json=USER)
    r = await client.get("/api/readings/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


async def test_create_reading_validation(client):
    await client.post("/api/auth/register", json=USER)
    r = await client.post("/api/readings", json={"question": ""})
    assert r.status_code == 422


async def test_reading_includes_matched_news_event(client, monkeypatch):
    from app.services import news

    async def recent_news(_market):
        return [
            news.NewsItem(
                headline="Alpha launches a new product", url="https://news.example/alpha"
            )
        ]

    monkeypatch.setattr(news, "recent_news", recent_news)
    from app.services import advice

    async def unavailable(*_args, **_kwargs):
        raise RuntimeError("exercise deterministic fallback")

    monkeypatch.setattr(advice, "_gemini_advice", unavailable)
    await client.post("/api/auth/register", json=USER)

    response = await client.post("/api/readings", json={"market": "stocks"})

    assert response.status_code == 201
    body = response.json()
    assert body["asset"]["symbol"] == "AAAA"
    assert body["event_headline"] == "Alpha launches a new product"
    assert body["event_url"] == "https://news.example/alpha"

    persisted = await client.get(f"/api/readings/{body['id']}")
    assert persisted.json()["event_headline"] == body["event_headline"]
    assert persisted.json()["event_url"] == body["event_url"]


async def test_reading_without_matching_news_has_no_event(client, monkeypatch):
    from app.services import news

    async def recent_news(_market):
        return [news.NewsItem(headline="Oil prices rise", url="https://news.example/oil")]

    monkeypatch.setattr(news, "recent_news", recent_news)
    from app.services import advice

    async def unavailable(*_args, **_kwargs):
        raise RuntimeError("exercise deterministic fallback")

    monkeypatch.setattr(advice, "_gemini_advice", unavailable)
    await client.post("/api/auth/register", json=USER)

    response = await client.post("/api/readings", json={"market": "stocks"})

    assert response.status_code == 201
    body = response.json()
    assert body["asset"]["symbol"] in {"AAAA", "BBBB"}
    assert body["event_headline"] is None
    assert body["event_url"] is None


async def test_reading_continues_when_news_is_empty(client, monkeypatch):
    from app.services import advice, news

    async def recent_news(_market):
        return []

    async def unavailable(*_args, **_kwargs):
        raise RuntimeError("exercise deterministic fallback")

    monkeypatch.setattr(news, "recent_news", recent_news)
    monkeypatch.setattr(advice, "_gemini_advice", unavailable)
    await client.post("/api/auth/register", json=USER)

    response = await client.post("/api/readings", json={"market": "crypto"})

    assert response.status_code == 201
    body = response.json()
    assert body["event_headline"] is None
    assert body["event_url"] is None


async def test_rapid_readings_share_news_fetch_within_cache_ttl(client, monkeypatch):
    from types import SimpleNamespace

    from app.services import advice, news

    categories_fetched = []

    class EmptyNewsResponse:
        status_code = 200

        def json(self):
            return []

    class FakeAsyncClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url, *, params):
            categories_fetched.append(params["category"])
            return EmptyNewsResponse()

    async def unavailable(*_args, **_kwargs):
        raise RuntimeError("exercise deterministic fallback")

    monkeypatch.setattr(news, "_cache", {})
    monkeypatch.setattr(news, "_locks", {})
    monkeypatch.setattr(
        news, "get_settings", lambda: SimpleNamespace(finnhub_api_key="test-key")
    )
    monkeypatch.setattr(news, "httpx", SimpleNamespace(AsyncClient=FakeAsyncClient))
    monkeypatch.setattr(advice, "_gemini_advice", unavailable)
    await client.post("/api/auth/register", json=USER)

    for _ in range(5):
        response = await client.post("/api/readings", json={"market": "stocks"})
        assert response.status_code == 201
        assert response.json()["event_headline"] is None

    assert categories_fetched == ["general"]


@pytest.mark.parametrize(
    ("model_headline", "expected_headline", "expected_url"),
    [
        (
            "Apple announces new product",
            "Apple announces new product",
            "https://news.example/apple",
        ),
        ("Unlisted market rumor", None, None),
    ],
)
async def test_gemini_event_is_validated_against_fetched_news(
    client, monkeypatch, model_headline, expected_headline, expected_url
):
    import json
    from types import SimpleNamespace

    from google import genai

    from app.services import advice, news

    async def recent_news(_market):
        return [
            news.NewsItem(
                headline="Apple announces new product",
                url="https://news.example/apple",
            )
        ]

    monkeypatch.setattr(news, "recent_news", recent_news)
    monkeypatch.setattr(
        advice, "get_settings", lambda: SimpleNamespace(gemini_api_key="test-key")
    )
    generated = json.dumps(
        {
            "side": "short",
            "asset_symbol": "BBBB",
            "event_headline": model_headline,
            "reasoning": "The spread points to a difficult period.",
            "cards": [
                {"position": position, "narrative": f"{position} narrative"}
                for position in ("past", "present", "future")
            ],
        }
    )

    model_names = []

    class FakeModels:
        async def generate_content(self, **kwargs):
            model_names.append(kwargs["model"])
            return SimpleNamespace(text=generated)

    fake_client = SimpleNamespace(aio=SimpleNamespace(models=FakeModels()))
    monkeypatch.setattr(genai, "Client", lambda **_kwargs: fake_client)
    await client.post("/api/auth/register", json=USER)

    response = await client.post("/api/readings", json={"market": "stocks"})

    assert response.status_code == 201
    body = response.json()
    assert body["asset"]["symbol"] == "BBBB"
    assert body["event_headline"] == expected_headline
    assert body["event_url"] == expected_url
    if expected_headline:
        assert expected_headline in body["interpretation"]
    assert model_names == ["gemini-3.5-flash-lite"]
