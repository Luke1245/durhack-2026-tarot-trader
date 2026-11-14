from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import TarotCard
from ..schemas import CardResponse

router = APIRouter(tags=["cards"])


@router.get("/cards", response_model=list[CardResponse])
async def list_cards(session: AsyncSession = Depends(get_session)) -> list[TarotCard]:
    return list((await session.scalars(select(TarotCard).order_by(TarotCard.id))).all())
