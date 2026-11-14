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

    # test cards are all "yes" -> score >= 0 -> long; fallback still advises
    assert body["side"] == "long"
    assert body["asset"]["symbol"] in {"AAAA", "BBBB"}
    assert all(c["narrative"] for c in body["cards"])


async def test_gemini_advice_used_when_available(client, monkeypatch):
    from app.services import advice

    async def fake_gemini(drawn, assets):
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

    async def broken(drawn, assets):
        raise RuntimeError("quota exceeded")

    monkeypatch.setattr(advice, "_gemini_advice", broken)
    body = await _draw(client)
    assert body["side"] in {"long", "short"}
    assert body["asset"] is not None


async def test_malformed_gemini_falls_back(client, monkeypatch):
    # wrong card count must not 500 — it degrades to the fallback
    from app.services import advice

    async def malformed(drawn, assets):
        raise ValueError("zip length mismatch stands in for malformed output")

    monkeypatch.setattr(advice, "_gemini_advice", malformed)
    body = await _draw(client)
    assert body["side"] in {"long", "short"}
    assert len(body["cards"]) == 3
