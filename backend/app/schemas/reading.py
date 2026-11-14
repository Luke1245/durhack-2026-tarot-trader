from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Card(BaseModel):
    name: str
    position: str  # e.g. "past", "present", "future"
    reversed_: bool = Field(alias="reversed", serialization_alias="reversed")

    model_config = {"populate_by_name": True}


class ReadingCreate(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class ReadingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    question: str
    cards: list[Card]
    interpretation: str
    created_at: datetime
