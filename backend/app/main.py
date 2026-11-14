import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import Base, SessionLocal, engine
from .models import (  # noqa: F401  (register all tables for CREATE TABLE / migrations)
    Asset,
    PortfolioSnapshot,
    Position,
    Reading,
    ReadingCard,
    Session,
    TarotCard,
    User,
)
from .routers import api_router

SNAPSHOT_INTERVAL_SECONDS = 300


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _snapshot_loop() -> None:
    import logging

    from .services import portfolio as portfolio_service

    logger = logging.getLogger("tarot-trader.snapshots")
    while True:
        await asyncio.sleep(SNAPSHOT_INTERVAL_SECONDS)
        async with SessionLocal() as session:
            try:
                await portfolio_service.snapshot_all_users(session)
            except Exception:
                logger.exception("snapshot cycle failed")  # keep the demo alive, but visible


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    task = asyncio.create_task(_snapshot_loop())
    yield
    task.cancel()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Tarot Trader API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
