from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .asset import AssetResponse

SpreadPosition = Literal["past", "present", "future"]


class ReadingCreate(BaseModel):
    question: str = Field(default="What do the cards advise?", min_length=1, max_length=500)
    market: Literal["all", "stocks", "crypto"] = "all"


class DrawnCard(BaseModel):
    card_id: int
    name: str
    image_path: str | None
    position: SpreadPosition
    reversed: bool
    meaning: str
    narrative: str | None = None


class ReadingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    question: str
    interpretation: str
    created_at: datetime
    side: Literal["long", "short"] | None
    asset: AssetResponse | None
    event_headline: str | None
    event_url: str | None
    cards: list[DrawnCard]
