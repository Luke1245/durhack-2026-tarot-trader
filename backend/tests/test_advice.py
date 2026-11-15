import pytest

pytestmark = pytest.mark.anyio

USER = {"email": "advice@example.com", "name": "Advice", "password": "supersecret1"}


async def _draw(client):
    await client.post("/api/auth/register", json=USER)
    return (await client.post("/api/readings", json={})).json()


async def test_fallback_advice_when_no_gemini(client, monkeypatch):
    from types import SimpleNamespace

    # neutralize the real key from .env so the fallback path is exercised
    monkeypatch.setattr("app.services.advice.get_settings", lambda: SimpleNamespace(gemini_api_key=""))
    body = await _draw(client)

    # The fixture's cards all vote yes, but reversed cards invert that verdict.
    reversed_count = sum(card["reversed"] for card in body["cards"])
    expected_side = "short" if reversed_count >= 2 else "long"
    assert body["side"] == expected_side
    assert body["asset"]["symbol"] in {"AAAA", "BBBB"}
    assert all(c["narrative"] for c in body["cards"])
    assert all(card["meaning"] in body["interpretation"] for card in body["cards"])
    assert "Together, these three meanings" in body["interpretation"]


async def test_gemini_advice_used_when_available(client, monkeypatch):
    from app.services import advice

    async def fake_gemini(drawn, assets, news_items):
        chosen = next(a for a in assets if a.symbol == "BBBB")
        return advice.Advice(
            side="short",
            asset=chosen,
            reasoning="The spread is ominous.",
            narratives={p: f"{p}: the tape agrees." for p in ("past", "present", "future")},
        )

    monkeypatch.setattr(advice, "_gemini_advice", fake_gemini)
    body = await _draw(client)

    assert body["side"] == "short"
    assert body["asset"]["symbol"] == "BBBB"
    past = next(c for c in body["cards"] if c["position"] == "past")
    assert past["narrative"] == "past: the tape agrees."


async def test_fallback_on_gemini_failure(client, monkeypatch):
    from app.services import advice

    async def broken(drawn, assets, news_items):
        raise RuntimeError("quota exceeded")

    monkeypatch.setattr(advice, "_gemini_advice", broken)
    body = await _draw(client)
    assert body["side"] in {"long", "short"}
    assert body["asset"] is not None


async def test_malformed_gemini_falls_back(client, monkeypatch):
    # wrong card count must not 500 — it degrades to the fallback
    from app.services import advice

    async def malformed(drawn, assets, news_items):
        raise ValueError("zip length mismatch stands in for malformed output")

    monkeypatch.setattr(advice, "_gemini_advice", malformed)
    body = await _draw(client)
    assert body["side"] in {"long", "short"}
    assert len(body["cards"]) == 3
