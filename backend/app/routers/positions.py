from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models import Position, User
from ..schemas import PortfolioResponse, PositionCreate, PositionResponse
from ..services import portfolio as portfolio_service
from ..services import positions as positions_service
from ..services import prices
from ..services.auth import get_current_user

router = APIRouter(tags=["positions"])


def to_response(position: Position, current_price: Decimal | None = None) -> PositionResponse:
    pnl = None
    if position.status == "open" and current_price is not None:
        pnl = positions_service.unrealized_pnl(position, current_price)
    elif position.status == "closed":
        pnl = positions_service.realized_pnl(position)
    return PositionResponse(
        id=position.id,
        asset_id=position.asset_id,
        asset_symbol=position.asset.symbol,
        asset_name=position.asset.name,
        side=position.side,
        quantity=position.quantity,
        entry_price=position.entry_price,
        status=position.status,
        exit_price=position.exit_price,
        opened_at=position.opened_at,
        closed_at=position.closed_at,
        current_price=current_price,
        pnl=pnl,
    )


@router.post("/positions", response_model=PositionResponse, status_code=201)
async def create_position(
    payload: PositionCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> PositionResponse:
    position = await positions_service.open_position(session, user.id, payload)
    position = await positions_service.get_position(session, user.id, position.id)
    await portfolio_service.snapshot_now(session, user.id)
    return to_response(position, await prices.current_price(position.asset.quote_symbol))


@router.get("/positions", response_model=list[PositionResponse])
async def list_positions(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[PositionResponse]:
    positions = list(
        (
            await session.scalars(
                select(Position)
                .where(Position.user_id == user.id)
                .options(selectinload(Position.asset))
                .order_by(Position.opened_at.desc())
            )
        ).all()
    )
    symbols = [p.asset.quote_symbol for p in positions if p.status == "open"]
    quotes = await prices.prices_for(symbols) if symbols else {}
    return [to_response(p, quotes.get(p.asset.quote_symbol)) for p in positions]


@router.post("/positions/{position_id}/close", response_model=PositionResponse)
async def close_position(
    position_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> PositionResponse:
    position = await positions_service.close_position(session, user.id, position_id)
    await portfolio_service.snapshot_now(session, user.id)
    return to_response(position)


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> PortfolioResponse:
    value = await portfolio_service.compute_value(session, user.id)
    await portfolio_service.maybe_snapshot(session, user.id)
    history = await portfolio_service.history(session, user.id)
    return PortfolioResponse(
        value=value,
        history=[
            {"taken_at": h.taken_at, "value": h.value} for h in history
        ],
    )
