import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Reading
from ..schemas import ReadingCreate

DECK = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World",
]
POSITIONS = ["past", "present", "future"]


async def create_reading(session: AsyncSession, payload: ReadingCreate) -> Reading:
    drawn = random.sample(DECK, 3)
    cards = [
        {"name": name, "position": pos, "reversed": random.random() < 0.3}
        for name, pos in zip(drawn, POSITIONS, strict=True)
    ]
    interpretation = (
        f"Regarding \"{payload.question}\": {drawn[0]} in the past, "
        f"{drawn[1]} in the present, {drawn[2]} in the future."
    )
    reading = Reading(question=payload.question, cards=cards, interpretation=interpretation)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


async def get_reading(session: AsyncSession, reading_id: UUID) -> Reading | None:
    return await session.scalar(select(Reading).where(Reading.id == reading_id))
