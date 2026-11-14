from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True)  # e.g. AAPL
    name: Mapped[str] = mapped_column(String(200))

    positions: Mapped[list["Position"]] = relationship(back_populates="asset")
