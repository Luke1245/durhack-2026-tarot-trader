import pytest

pytestmark = pytest.mark.anyio


async def test_list_cards(client):
    r = await client.get("/api/cards")
    assert r.status_code == 200
    cards = r.json()
    assert len(cards) == 4  # seeded by the client fixture
    assert cards[0]["name"] == "The Fool"
    assert {"id", "name", "image_path"} <= cards[0].keys()
