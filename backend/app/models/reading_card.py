from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

SPREAD_POSITIONS = ("past", "present", "future")


class ReadingCard(Base):
    """One drawn card in a reading: which card, spread position, orientation."""

    __tablename__ = "reading_cards"

    reading_id: Mapped[UUID] = mapped_column(
        ForeignKey("readings.id", ondelete="CASCADE"), primary_key=True
    )
    card_id: Mapped[int] = mapped_column(ForeignKey("tarot_cards.id"), primary_key=True, index=True)
    position: Mapped[str] = mapped_column(String(10))  # past | present | future
    reversed: Mapped[bool] = mapped_column(Boolean, default=False)

    reading: Mapped["Reading"] = relationship(back_populates="drawn_cards")
    card: Mapped["TarotCard"] = relationship()
