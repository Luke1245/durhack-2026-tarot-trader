import pytest

pytestmark = pytest.mark.anyio

USER = {"email": "Ada@Example.com", "name": "Ada", "password": "supersecret1"}


async def test_register_sets_cookie_and_me(client):
    r = await client.post("/api/auth/register", json=USER)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "ada@example.com"  # lowercased
    assert "session" in r.cookies

    r2 = await client.get("/api/auth/me")
    assert r2.status_code == 200
    assert r2.json()["email"] == "ada@example.com"


async def test_register_duplicate_email(client):
    assert (await client.post("/api/auth/register", json=USER)).status_code == 201
    r = await client.post("/api/auth/register", json=USER)
    assert r.status_code == 409


async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json=USER)
    client.cookies.clear()
    r = await client.post(
        "/api/auth/login", json={"email": "ada@example.com", "password": "wrongpass1"}
    )
    assert r.status_code == 401


async def test_login_after_logout(client):
    await client.post("/api/auth/register", json=USER)
    assert (await client.get("/api/auth/me")).status_code == 200

    r = await client.post("/api/auth/logout")
    assert r.status_code == 204
    assert (await client.get("/api/auth/me")).status_code == 401

    r = await client.post("/api/auth/login", json={"email": "ada@example.com", "password": "supersecret1"})
    assert r.status_code == 200
    assert (await client.get("/api/auth/me")).status_code == 200


async def test_password_too_short(client):
    r = await client.post("/api/auth/register", json={**USER, "password": "short"})
    assert r.status_code == 422
