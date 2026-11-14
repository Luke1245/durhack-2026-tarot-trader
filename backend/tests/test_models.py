import pytest
from sqlalchemy import select

from datetime import datetime

from app.db import Base, SessionLocal, engine
from app.models import Asset, Position, Reading, ReadingCard, Session, TarotCard, User

pytestmark = pytest.mark.anyio


@pytest.fixture
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def test_user_session_position_roundtrip(session):
    user = User(email="ada@example.com", name="Ada", password_hash="hash")
    card = TarotCard(name="The Sun", arcana="major", upright="u", reversed_="r",
                     love="l", career="c", yes_no="yes")
    asset = Asset(symbol="AAPL", name="Apple Inc.")
    session.add_all([user, card, asset])
    await session.flush()

    token = Session(user_id=user.id, token_hash="a" * 64, expires_at=datetime(2027, 1, 1))
    reading = Reading(user_id=user.id, question="q", interpretation="i")
    session.add_all([token, reading])
    await session.flush()

    draw = ReadingCard(reading_id=reading.id, card_id=card.id, position="past", reversed=False)
    position = Position(
        user_id=user.id, asset_id=asset.id, reading_id=reading.id,
        side="short", quantity=2, entry_price=190.5,
    )
    session.add_all([draw, position])
    await session.commit()

    loaded = await session.scalar(select(Position).where(Position.id == position.id))
    assert loaded is not None
    assert loaded.side == "short"
    assert loaded.status == "open"
    assert loaded.reading_id == reading.id
    assert loaded.exit_price is None and loaded.closed_at is None

    draws = (await session.scalars(select(ReadingCard).where(ReadingCard.reading_id == reading.id))).all()
    assert len(draws) == 1
    assert draws[0].card.name == "The Sun"
