from pydantic import BaseModel


class CardResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    image_path: str | None
