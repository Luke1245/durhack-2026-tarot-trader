from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question: Mapped[str] = mapped_column(Text)
    interpretation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    # the Advice (Gemini or fallback): direction and chosen asset; null pre-advice
    side: Mapped[str | None] = mapped_column(String(5))
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), index=True)
    # the news event that motivated the pick; null when the pick was event-less
    event_headline: Mapped[str | None] = mapped_column(Text)
    event_url: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="readings")
    asset: Mapped["Asset | None"] = relationship()
    drawn_cards: Mapped[list["ReadingCard"]] = relationship(
        back_populates="reading", cascade="all, delete-orphan"
    )
