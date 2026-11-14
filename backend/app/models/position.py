from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

SIDES = ("long", "short")
POSITION_STATUSES = ("open", "closed")


class Position(Base):
    """A paper trade. Entry/exit prices are recorded at the moment of the action;
    unrealized PnL for open positions is computed at read time (ADR-0001)."""

    __tablename__ = "positions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)
    reading_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("readings.id", ondelete="SET NULL"), index=True
    )
    side: Mapped[str] = mapped_column(String(5))  # long | short
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    entry_price: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    status: Mapped[str] = mapped_column(String(10), default="open")
    exit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 8))
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="positions")
    asset: Mapped["Asset"] = relationship(back_populates="positions")
