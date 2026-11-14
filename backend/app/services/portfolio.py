from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import PortfolioSnapshot, Position
from . import prices
from .positions import marked_value, realized_pnl

SNAPSHOT_STALE_AFTER = timedelta(minutes=5)


async def compute_value(session: AsyncSession, user_id: UUID) -> Decimal:
    """Portfolio value on a continuous basis: open positions at marked value,
    closed positions at cost basis + realized PnL (liquidation proceeds), so
    closing a position never cliff-drops the graph."""
    positions = list(
        (
            await session.scalars(
                select(Position)
                .where(Position.user_id == user_id)
                .options(selectinload(Position.asset))
            )
        ).all()
    )
    quotes = await prices.prices_for([p.asset.quote_symbol for p in positions]) if positions else {}

    value = Decimal(0)
    for p in positions:
        if p.status == "open":
            # unavailable quote -> value at entry until the feed recovers
            value += marked_value(p, quotes.get(p.asset.quote_symbol) or p.entry_price)
        else:
            # continuous basis: cost basis + realized PnL (= liquidation proceeds),
            # so closing a position doesn't cliff-drop the portfolio value
            value += p.entry_price * p.quantity + realized_pnl(p)
    return value


async def maybe_snapshot(session: AsyncSession, user_id: UUID) -> None:
    """Lazy snapshot write: record value if the latest snapshot is stale."""
    latest = await session.scalar(
        select(PortfolioSnapshot)
        .where(PortfolioSnapshot.user_id == user_id)
        .order_by(PortfolioSnapshot.taken_at.desc())
        .limit(1)
    )
    now = datetime.now(timezone.utc)
    if latest is not None:
        taken_at = latest.taken_at
        if taken_at.tzinfo is None:
            taken_at = taken_at.replace(tzinfo=timezone.utc)
        if now - taken_at < SNAPSHOT_STALE_AFTER:
            return
    await snapshot_now(session, user_id)


async def snapshot_now(session: AsyncSession, user_id: UUID) -> None:
    """Unconditional snapshot — used right after a position opens or closes so
    the portfolio value/graph reflect the trade immediately."""
    value = await compute_value(session, user_id)
    session.add(PortfolioSnapshot(user_id=user_id, value=value, taken_at=datetime.now(timezone.utc)))
    await session.commit()


async def history(session: AsyncSession, user_id: UUID) -> list[PortfolioSnapshot]:
    rows = (
        await session.scalars(
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.user_id == user_id)
            .order_by(PortfolioSnapshot.taken_at)
        )
    ).all()
    return list(rows)


async def snapshot_all_users(session: AsyncSession) -> None:
    """Scheduled task: snapshot every user that has any position."""
    from ..models import User

    user_ids = list(
        (await session.scalars(select(Position.user_id).distinct())).all()
    )
    for user_id in user_ids:
        await maybe_snapshot(session, user_id)
