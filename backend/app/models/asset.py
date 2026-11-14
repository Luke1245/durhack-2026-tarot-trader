from typing import Literal

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. AAPL, BTC
    name: Mapped[str] = mapped_column(String(200))
    # provider symbol for quotes; NULL means symbol is the quote symbol (stocks)
    finnhub_symbol: Mapped[str | None] = mapped_column(String(40))

    positions: Mapped[list["Position"]] = relationship(back_populates="asset")

    @property
    def quote_symbol(self) -> str:
        return self.finnhub_symbol or self.symbol

    @property
    def market(self) -> Literal["stocks", "crypto"]:
        return "crypto" if self.finnhub_symbol else "stocks"
