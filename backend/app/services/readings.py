import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SPREAD_POSITIONS, Reading, ReadingCard, TarotCard, User
from ..schemas import ReadingCreate

# Temporary until auth (step 3): readings attach to an auto-provisioned demo user.
DEMO_EMAIL = "demo@tarot-trader.local"


async def _get_or_create_demo_user(session: AsyncSession) -> User:
    user = await session.scalar(select(User).where(User.email == DEMO_EMAIL))
    if user is None:
        user = User(email=DEMO_EMAIL, name="Demo User", password_hash="!")
        session.add(user)
        await session.flush()
    return user


async def create_reading(session: AsyncSession, payload: ReadingCreate) -> Reading:
    user = await _get_or_create_demo_user(session)

    cards = (await session.scalars(select(TarotCard))).all()
    if len(cards) < len(SPREAD_POSITIONS):
        raise RuntimeError("tarot_cards is not seeded; run scripts/import_cards.py")
    drawn = random.sample(list(cards), len(SPREAD_POSITIONS))

    parts = []
    reading_cards = []
    for card, position in zip(drawn, SPREAD_POSITIONS, strict=True):
        is_reversed = random.random() < 0.3
        meaning = card.reversed_ if is_reversed else card.upright
        parts.append(f"{card.name} ({position}{', reversed' if is_reversed else ''}): {meaning}")
        reading_cards.append(
            ReadingCard(card_id=card.id, position=position, reversed=is_reversed)
        )

    reading = Reading(
        user_id=user.id,
        question=payload.question,
        interpretation=f"Regarding \"{payload.question}\" — " + "; ".join(parts),
    )
    reading.drawn_cards.extend(reading_cards)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


async def get_reading(session: AsyncSession, reading_id: UUID) -> Reading | None:
    return await session.get(Reading, reading_id)
