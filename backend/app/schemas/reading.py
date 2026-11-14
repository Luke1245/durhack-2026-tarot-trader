from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

SpreadPosition = Literal["past", "present", "future"]


class ReadingCreate(BaseModel):
    question: str = Field(default="What do the cards advise?", min_length=1, max_length=500)


class DrawnCard(BaseModel):
    card_id: int
    name: str
    image_path: str | None
    position: SpreadPosition
    reversed: bool
    meaning: str


class ReadingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    question: str
    interpretation: str
    created_at: datetime
    cards: list[DrawnCard]
