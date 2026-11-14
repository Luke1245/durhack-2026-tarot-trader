from pydantic import BaseModel


class AssetResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    symbol: str
    name: str
