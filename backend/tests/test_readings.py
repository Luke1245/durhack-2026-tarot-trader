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
