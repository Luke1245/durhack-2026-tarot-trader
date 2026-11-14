import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SPREAD_POSITIONS, Asset, Reading, ReadingCard, TarotCard, User
from ..schemas import ReadingCreate
from . import advice as advice_service


async def create_reading(session: AsyncSession, user: User, payload: ReadingCreate) -> Reading:
    cards = (await session.scalars(select(TarotCard))).all()
    if len(cards) < len(SPREAD_POSITIONS):
        raise RuntimeError("tarot_cards is not seeded; run scripts/import_cards.py")
    drawn = random.sample(list(cards), len(SPREAD_POSITIONS))

    drawn_oriented: list[tuple[TarotCard, str, bool]] = []
    reading_cards = []
    for card, position in zip(drawn, SPREAD_POSITIONS, strict=True):
        is_reversed = random.random() < 0.3
        drawn_oriented.append((card, position, is_reversed))
        reading_cards.append(
            ReadingCard(card_id=card.id, position=position, reversed=is_reversed)
        )

    assets = list((await session.scalars(select(Asset))).all())
    if payload.market != "all":
        assets = [a for a in assets if a.market == payload.market]
    advice = await advice_service.get_advice(drawn_oriented, assets)
    for rc in reading_cards:
        rc.narrative = advice.narratives[rc.position]

    reading = Reading(
        user_id=user.id,
        question=payload.question,
        interpretation=(
            f"Regarding \"{payload.question}\": {advice.reasoning}"
            if advice.asset
            else advice.reasoning
        ),
        side=advice.side,
        asset_id=advice.asset.id if advice.asset else None,
    )
    reading.drawn_cards.extend(reading_cards)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


async def get_reading(session: AsyncSession, reading_id: UUID) -> Reading | None:
    return await session.get(Reading, reading_id)
