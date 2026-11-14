from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class TarotCard(Base):
    """One of the 78 fixed reference cards. Read-only, identical for all users."""

    __tablename__ = "tarot_cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    arcana: Mapped[str] = mapped_column(String(10))  # "major" | "minor"
    suit: Mapped[str | None] = mapped_column(String(20))  # null for Major Arcana
    rank: Mapped[str | None] = mapped_column(String(20))
    upright: Mapped[str] = mapped_column(Text)
    reversed_: Mapped[str] = mapped_column("reversed", Text)
    love: Mapped[str] = mapped_column(Text)
    career: Mapped[str] = mapped_column(Text)
    yes_no: Mapped[str] = mapped_column(String(20))
    element: Mapped[str | None] = mapped_column(String(20))
    zodiac: Mapped[str | None] = mapped_column(String(50))
    guide_url: Mapped[str | None] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(Text)
