from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class PortfolioSnapshot(Base):
    """Point-in-time portfolio value for the performance graph (ADR-0001 amendment)."""

    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped["User"] = relationship()
