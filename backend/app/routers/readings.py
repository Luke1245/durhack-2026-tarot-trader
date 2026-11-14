from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models import Reading, ReadingCard
from ..schemas import DrawnCard, ReadingCreate, ReadingResponse
from ..services import readings as readings_service

router = APIRouter(tags=["readings"])


def _to_response(reading: Reading) -> ReadingResponse:
    return ReadingResponse(
        id=reading.id,
        question=reading.question,
        interpretation=reading.interpretation,
        created_at=reading.created_at,
        cards=[
            DrawnCard(
                card_id=rc.card.id,
                name=rc.card.name,
                position=rc.position,
                reversed=rc.reversed,
                meaning=rc.card.reversed_ if rc.reversed else rc.card.upright,
            )
            for rc in reading.drawn_cards
        ],
    )


async def _load(session: AsyncSession, reading_id: UUID) -> Reading | None:
    return await session.scalar(
        select(Reading)
        .where(Reading.id == reading_id)
        .options(selectinload(Reading.drawn_cards).selectinload(ReadingCard.card))
    )


@router.post("/readings", response_model=ReadingResponse, status_code=201)
async def create_reading(
    payload: ReadingCreate,
    session: AsyncSession = Depends(get_session),
) -> ReadingResponse:
    reading = await readings_service.create_reading(session, payload)
    return _to_response(await _load(session, reading.id))


@router.get("/readings/{reading_id}", response_model=ReadingResponse)
async def get_reading(
    reading_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ReadingResponse:
    reading = await _load(session, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return _to_response(reading)
