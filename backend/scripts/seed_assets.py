"""Seed the tradeable assets table (idempotent upsert by symbol).

Usage:
    uv run python scripts/seed_assets.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

ASSETS = [
    ("AAPL", "Apple Inc."), ("MSFT", "Microsoft Corp."), ("NVDA", "NVIDIA Corp."),
    ("AMZN", "Amazon.com Inc."), ("GOOGL", "Alphabet Inc."), ("META", "Meta Platforms"),
    ("TSLA", "Tesla Inc."), ("JPM", "JPMorgan Chase"), ("V", "Visa Inc."),
    ("XOM", "Exxon Mobil"), ("NFLX", "Netflix Inc."), ("AMD", "Advanced Micro Devices"),
    ("LLY", "Eli Lilly"), ("COST", "Costco Wholesale"), ("DIS", "Walt Disney"),
]


async def main() -> None:
    from app.db import Base, SessionLocal, engine
    from app.models import Asset

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    added = 0
    async with SessionLocal() as session:
        existing = {a.symbol for a in (await session.scalars(select(Asset))).all()}
        for symbol, name in ASSETS:
            if symbol not in existing:
                session.add(Asset(symbol=symbol, name=name))
                added += 1
        await session.commit()
    print(f"added {added} assets, total {len(ASSETS)}")


if __name__ == "__main__":
    asyncio.run(main())
