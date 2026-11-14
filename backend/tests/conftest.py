import os

os.environ["APP_DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["APP_GEMINI_API_KEY"] = ""  # never call the real model from tests

import pytest
from httpx import ASGITransport, AsyncClient

from app.db import Base, SessionLocal, engine
from app.main import create_app
from app.models import Asset, TarotCard


def make_test_assets() -> list[Asset]:
    return [Asset(symbol="AAAA", name="Alpha Co"), Asset(symbol="BBBB", name="Beta Co")]


def make_test_cards() -> list[TarotCard]:
    return [
        TarotCard(
            name=name, arcana="major", suit=None, rank=None,
            upright=f"{name} upright meaning", reversed_=f"{name} reversed meaning",
            love=f"{name} love meaning", career=f"{name} career meaning",
            yes_no="yes", element="Fire", zodiac="Aries", guide_url=None, image_path=None,
        )
        for name in ("The Fool", "The Magician", "The High Priestess", "The Empress")
    ]


@pytest.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        session.add_all(make_test_cards() + make_test_assets())
        await session.commit()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
