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
