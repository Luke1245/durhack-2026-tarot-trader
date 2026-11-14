from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Asset
from ..schemas import AssetResponse

router = APIRouter(tags=["assets"])


@router.get("/assets", response_model=list[AssetResponse])
async def list_assets(session: AsyncSession = Depends(get_session)) -> list[Asset]:
    return list((await session.scalars(select(Asset).order_by(Asset.symbol))).all())
