from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class PositionCreate(BaseModel):
    asset_id: int
    side: Literal["long", "short"]
    quantity: Decimal = Field(gt=0)
    reading_id: UUID | None = None


class PositionResponse(BaseModel):
    id: UUID
    asset_id: int
    asset_symbol: str
    side: Literal["long", "short"]
    quantity: float
    entry_price: float
    status: Literal["open", "closed"]
    exit_price: float | None
    opened_at: datetime
    closed_at: datetime | None
    current_price: float | None = None  # open positions only
    pnl: float | None = None  # open: unrealized; closed: realized


class PortfolioPoint(BaseModel):
    taken_at: datetime
    value: float


class PortfolioResponse(BaseModel):
    value: float
    history: list[PortfolioPoint]
