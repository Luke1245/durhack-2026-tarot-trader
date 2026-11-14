"""Seed the 24/7 crypto assets (idempotent upsert by symbol).

Finnhub quotes crypto under BINANCE:<pair>; finnhub_symbol stores that
while symbol stays the clean display name.

Usage:
    uv run python scripts/seed_crypto.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

CRYPTO = [
    ("BTC", "Bitcoin", "BINANCE:BTCUSDT"),
    ("ETH", "Ethereum", "BINANCE:ETHUSDT"),
    ("SOL", "Solana", "BINANCE:SOLUSDT"),
    ("XRP", "XRP", "BINANCE:XRPUSDT"),
    ("DOGE", "Dogecoin", "BINANCE:DOGEUSDT"),
    ("AVAX", "Avalanche", "BINANCE:AVAXUSDT"),
    ("LINK", "Chainlink", "BINANCE:LINKUSDT"),
    ("ADA", "Cardano", "BINANCE:ADAUSDT"),
]


async def main() -> None:
    from app.db import Base, SessionLocal, engine
    from app.models import Asset

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    added = 0
    async with SessionLocal() as session:
        existing = {a.symbol: a for a in (await session.scalars(select(Asset))).all()}
        for symbol, name, finnhub_symbol in CRYPTO:
            asset = existing.get(symbol)
            if asset is None:
                session.add(Asset(symbol=symbol, name=name, finnhub_symbol=finnhub_symbol))
                added += 1
            elif asset.finnhub_symbol != finnhub_symbol:
                asset.finnhub_symbol = finnhub_symbol
        await session.commit()
        total = len((await session.scalars(select(Asset))).all())
    print(f"added {added} crypto assets ({total} assets total)")


if __name__ == "__main__":
    asyncio.run(main())
