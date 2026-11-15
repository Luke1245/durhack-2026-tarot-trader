from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models import Asset, PortfolioSnapshot, Position

pytestmark = pytest.mark.anyio

USER = {"email": "trader@example.com", "name": "Trader", "password": "supersecret1"}

# deterministic "market": AAPL always 200, TSLA always 100
FAKE_PRICES = {"AAPL": Decimal("200"), "TSLA": Decimal("100")}


@pytest.fixture
def fake_prices(monkeypatch):
    from app.services import prices

    async def fake_current_price(symbol: str) -> Decimal:
        if symbol not in FAKE_PRICES:
            raise LookupError(symbol)
        return FAKE_PRICES[symbol]

    async def fake_prices_for(symbols):
        return {s: await fake_current_price(s) for s in symbols}

    monkeypatch.setattr(prices, "current_price", fake_current_price)
    monkeypatch.setattr(prices, "prices_for", fake_prices_for)
    # bust the module-level cache so fake values never leak between tests
    prices._cache.clear()
    return FAKE_PRICES


async def _setup_assets(client):
    from app.db import SessionLocal

    async with SessionLocal() as session:
        session.add_all([Asset(symbol="AAPL", name="Apple"), Asset(symbol="TSLA", name="Tesla")])
        await session.commit()


async def _asset_id(symbol: str) -> int:
    from app.db import SessionLocal

    async with SessionLocal() as session:
        return (await session.scalar(select(Asset).where(Asset.symbol == symbol))).id


async def test_open_position_uses_current_price(client, fake_prices):
    await client.post("/api/auth/register", json=USER)
    await _setup_assets(client)

    r = await client.post(
        "/api/positions",
        json={"asset_id": await _asset_id("AAPL"), "side": "long", "quantity": "2"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["entry_price"] == 200  # from the stub, not the DB default
    assert body["status"] == "open"
    assert body["pnl"] == 0  # current == entry
    assert body["asset_symbol"] == "AAPL"
    assert body["asset_name"] == "Apple"


async def test_short_position_pnl_direction(client, fake_prices):
    await client.post("/api/auth/register", json=USER)
    await _setup_assets(client)

    r = await client.post(
        "/api/positions",
        json={"asset_id": await _asset_id("TSLA"), "side": "short", "quantity": "3"},
    )
    body = r.json()
    assert body["entry_price"] == 100

    # price "falls" to 90 -> short profits 3 * 10 = 30
    fake_prices["TSLA"] = Decimal("90")
    rid = body["id"]
    r2 = await client.get("/api/positions")
    position = next(p for p in r2.json() if p["id"] == rid)
    assert position["current_price"] == 90
    assert position["pnl"] == 30

    r3 = await client.post(f"/api/positions/{rid}/close")
    assert r3.status_code == 200
    closed = r3.json()
    assert closed["status"] == "closed"
    assert closed["exit_price"] == 90
    assert closed["pnl"] == 30

    # double close is rejected
    assert (await client.post(f"/api/positions/{rid}/close")).status_code == 409


async def test_portfolio_value_and_snapshot(client, fake_prices):
    await client.post("/api/auth/register", json=USER)
    await _setup_assets(client)
    await client.post(
        "/api/positions",
        json={"asset_id": await _asset_id("AAPL"), "side": "long", "quantity": "1"},
    )

    r = await client.get("/api/portfolio")
    assert r.status_code == 200
    body = r.json()
    # 1 AAPL @ entry 200, current 200 -> value 200
    assert body["value"] == 200
    assert len(body["history"]) >= 1  # lazy snapshot written

    # stale-check: a second read does not duplicate the snapshot
    r2 = await client.get("/api/portfolio")
    assert len(r2.json()["history"]) == len(body["history"])


async def test_portfolio_value_continuous_across_close(client, fake_prices):
    # closing must not cliff-drop value: closed contributes cost basis + realized PnL
    await client.post("/api/auth/register", json=USER)
    await _setup_assets(client)
    opened = (
        await client.post(
            "/api/positions",
            json={"asset_id": await _asset_id("AAPL"), "side": "long", "quantity": "1"},
        )
    ).json()
    before = (await client.get("/api/portfolio")).json()["value"]

    fake_prices["AAPL"] = Decimal("210")  # rises: +10 unrealized
    await client.post(f"/api/positions/{opened['id']}/close")
    after = (await client.get("/api/portfolio")).json()["value"]
    # closed basis: 200 cost + 10 realized = 210 (not just the 10 PnL)
    assert after == 210
    assert after == before + 10


async def test_open_and_close_write_snapshots(client, fake_prices):
    # each trade immediately adds a graph point so the portfolio reflects it
    await client.post("/api/auth/register", json=USER)
    await _setup_assets(client)
    hist0 = (await client.get("/api/portfolio")).json()["history"]

    opened = (
        await client.post(
            "/api/positions",
            json={"asset_id": await _asset_id("AAPL"), "side": "long", "quantity": "1"},
        )
    ).json()
    hist1 = (await client.get("/api/portfolio")).json()["history"]
    assert len(hist1) == len(hist0) + 1  # snapshot written on open

    await client.post(f"/api/positions/{opened['id']}/close")
    hist2 = (await client.get("/api/portfolio")).json()["history"]
    assert len(hist2) == len(hist1) + 1  # and on close


async def test_positions_require_auth(client):
    assert (await client.get("/api/positions")).status_code == 401
    assert (await client.get("/api/portfolio")).status_code == 401


async def test_unknown_asset_404(client, fake_prices):
    await client.post("/api/auth/register", json=USER)
    r = await client.post(
        "/api/positions", json={"asset_id": 99999, "side": "long", "quantity": "1"}
    )
    assert r.status_code == 404


async def test_foreign_reading_rejected(client, fake_prices):
    # user A draws a reading; user B cannot attach it to a position
    await client.post("/api/auth/register", json=USER)
    await _setup_assets(client)
    reading = (await client.post("/api/readings", json={})).json()

    client.cookies.clear()
    await client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "name": "Other", "password": "supersecret1"},
    )
    r = await client.post(
        "/api/positions",
        json={
            "asset_id": await _asset_id("AAPL"),
            "side": "long",
            "quantity": "1",
            "reading_id": reading["id"],
        },
    )
    assert r.status_code == 404
