import pytest

pytestmark = pytest.mark.anyio

USER = {"email": "cards@example.com", "name": "Cards", "password": "supersecret1"}


async def test_list_cards(client):
    r = await client.get("/api/cards")
    assert r.status_code == 200
    cards = r.json()
    assert len(cards) == 4  # seeded by the client fixture
    assert cards[0]["name"] == "The Fool"
    assert {"id", "name", "image_path"} <= cards[0].keys()


async def test_list_assets(client):
    await client.post("/api/auth/register", json=USER)
    from app.db import SessionLocal
    from app.models import Asset

    async with SessionLocal() as session:
        session.add(Asset(symbol="AAPL", name="Apple"))
        await session.commit()
    r = await client.get("/api/assets")
    assert r.status_code == 200
    symbols = {a["symbol"] for a in r.json()}
    assert {"AAAA", "BBBB", "AAPL"} <= symbols
