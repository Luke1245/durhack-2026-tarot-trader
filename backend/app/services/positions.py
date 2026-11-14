from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Asset, Position, Reading
from ..schemas import PositionCreate
from . import prices


async def open_position(
    session: AsyncSession, user_id: UUID, payload: PositionCreate
) -> Position:
    asset = await session.get(Asset, payload.asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    if payload.reading_id is not None:
        reading = await session.get(Reading, payload.reading_id)
        if reading is None or reading.user_id != user_id:
            raise HTTPException(status_code=404, detail="Reading not found")

    price = await prices.current_price(asset.quote_symbol)
    position = Position(
        user_id=user_id,
        asset_id=asset.id,
        reading_id=payload.reading_id,
        side=payload.side,
        quantity=payload.quantity,
        entry_price=price,
        status="open",
    )
    session.add(position)
    await session.commit()
    await session.refresh(position)
    return position


async def get_position(session: AsyncSession, user_id: UUID, position_id: UUID) -> Position:
    position = await session.scalar(
        select(Position)
        .where(Position.id == position_id, Position.user_id == user_id)
        .options(selectinload(Position.asset))
    )
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return position


async def close_position(session: AsyncSession, user_id: UUID, position_id: UUID) -> Position:
    position = await get_position(session, user_id, position_id)
    if position.status == "closed":
        raise HTTPException(status_code=409, detail="Position already closed")
    position.exit_price = await prices.current_price(position.asset.quote_symbol)
    position.status = "closed"
    position.closed_at = position.closed_at or datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(position)
    return position


def unrealized_pnl(position: Position, current: Decimal) -> Decimal:
    """Long profits when price rises; short profits when it falls."""
    diff = current - position.entry_price if position.side == "long" else position.entry_price - current
    return diff * position.quantity


def realized_pnl(position: Position) -> Decimal:
    if position.exit_price is None:
        return Decimal(0)
    diff = (
        position.exit_price - position.entry_price
        if position.side == "long"
        else position.entry_price - position.exit_price
    )
    return diff * position.quantity


def marked_value(position: Position, current: Decimal) -> Decimal:
    """Marked value of an open position: what closing it now would leave."""
    return position.entry_price * position.quantity + unrealized_pnl(position, current)
