from decimal import Decimal

import pytest

pytestmark = pytest.mark.anyio

USER = {"email": "crypto@example.com", "name": "Crypto", "password": "supersecret1"}


@pytest.fixture
def fake_prices(monkeypatch):
    from app.services import prices

    async def fake_current_price(symbol: str) -> Decimal:
        if symbol not in FAKE:
            raise LookupError(symbol)
        return FAKE[symbol]

    async def fake_prices_for(symbols):
        return {s: await fake_current_price(s) for s in symbols}

    monkeypatch.setattr(prices, "current_price", fake_current_price)
    monkeypatch.setattr(prices, "prices_for", fake_prices_for)
    prices._cache.clear()
    return FAKE


FAKE = {"BINANCE:BTCUSDT": Decimal("97000"), "AAPL": Decimal("200")}


async def _seed(client):
    from app.db import SessionLocal
    from app.models import Asset

    await client.post("/api/auth/register", json=USER)
    async with SessionLocal() as session:
        session.add_all(
            [
                Asset(symbol="AAPL", name="Apple", finnhub_symbol=None),
                Asset(symbol="BTC", name="Bitcoin", finnhub_symbol="BINANCE:BTCUSDT"),
            ]
        )
        await session.commit()


async def test_crypto_position_uses_finnhub_symbol(client, fake_prices):
    from sqlalchemy import select

    from app.db import SessionLocal
    from app.models import Asset

    await _seed(client)
    async with SessionLocal() as session:
        btc_id = (await session.scalar(select(Asset).where(Asset.symbol == "BTC"))).id

    r = await client.post(
        "/api/positions", json={"asset_id": btc_id, "side": "long", "quantity": "1"}
    )
    assert r.status_code == 201
    assert r.json()["entry_price"] == 97000  # via BINANCE:BTCUSDT, not "BTC"
    assert r.json()["asset_symbol"] == "BTC"  # display symbol stays clean


async def test_market_filter_limits_advice_universe(client, monkeypatch):
    from app.services import advice

    async def flaky(*a, **k):
        raise RuntimeError("force fallback")

    monkeypatch.setattr(advice, "_gemini_advice", flaky)
    await _seed(client)
    # NB: the shared fixture also seeds stock assets AAAA/BBBB

    r = await client.post("/api/readings", json={"market": "crypto"})
    assert r.status_code == 201
    assert r.json()["asset"]["symbol"] == "BTC"  # only crypto in the universe

    r2 = await client.post("/api/readings", json={"market": "stocks"})
    assert r2.json()["asset"]["symbol"] in {"AAPL", "AAAA", "BBBB"}
    assert r2.json()["asset"]["symbol"] != "BTC"

    r3 = await client.post("/api/readings", json={"market": "all"})
    assert r3.json()["asset"]["symbol"] in {"AAPL", "AAAA", "BBBB", "BTC"}


async def test_market_filter_validation(client):
    await _seed(client)
    r = await client.post("/api/readings", json={"market": "commodities"})
    assert r.status_code == 422
