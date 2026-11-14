from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    question: Mapped[str] = mapped_column(Text)
    cards: Mapped[list] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    interpretation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
