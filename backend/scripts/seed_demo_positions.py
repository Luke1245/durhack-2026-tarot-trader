"""Insert fake positions for a demo user so the portfolio page has data.

Creates (or reuses) demo@tarot-trader.dev / demo12345, opens 5 positions
across seeded assets at plausible entry prices, closes 1 with a profit.
Prices are hardcoded — the live feed only matters for current_price/PnL display.

Usage:
    uv run python scripts/seed_demo_positions.py
"""

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

DEMO_EMAIL = "demo@tarot-trader.dev"
DEMO_PASSWORD = "demo12345"

# (symbol, side, quantity, entry_price)
FAKE_POSITIONS = [
    ("AAPL", "long", "2", "212.40"),
    ("NVDA", "long", "5", "138.25"),
    ("TSLA", "short", "4", "248.50"),
    ("MSFT", "long", "1", "428.15"),
    ("AMD", "short", "10", "122.80"),
    ("NFLX", "long", "1", "887.60"),
]
# closed at a profit: bought 3 @ 155.20, sold @ 161.40
CLOSED = ("JPM", "long", "3", "155.20", "161.40")


async def main() -> None:
    from app.db import Base, SessionLocal, engine
    from app.models import Asset, Position, User
    from app.services.auth import password_hash

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == DEMO_EMAIL))
        if user is None:
            user = User(email=DEMO_EMAIL, name="Demo Trader", password_hash=password_hash.hash(DEMO_PASSWORD))
            session.add(user)
            await session.flush()

        existing = (
            await session.scalar(
                select(Position).where(Position.user_id == user.id).limit(1)
            )
        )
        if existing:
            print(f"demo user already has positions; delete them first if you want a fresh set ({DEMO_EMAIL})")
            return

        assets = {a.symbol: a for a in (await session.scalars(select(Asset))).all()}
        missing = {s for s, *_ in [*FAKE_POSITIONS, CLOSED]} - assets.keys()
        if missing:
            raise SystemExit(f"assets not seeded: {missing} (run scripts/seed_assets.py)")

        now = datetime.now(timezone.utc)
        for i, (symbol, side, qty, entry) in enumerate(FAKE_POSITIONS):
            session.add(
                Position(
                    user_id=user.id,
                    asset_id=assets[symbol].id,
                    side=side,
                    quantity=Decimal(qty),
                    entry_price=Decimal(entry),
                    status="open",
                    opened_at=now - timedelta(days=random.randint(1, 10), hours=random.randint(1, 12)),
                )
            )
        symbol, side, qty, entry, exit_ = CLOSED
        session.add(
            Position(
                user_id=user.id,
                asset_id=assets[symbol].id,
                side=side,
                quantity=Decimal(qty),
                entry_price=Decimal(entry),
                exit_price=Decimal(exit_),
                status="closed",
                opened_at=now - timedelta(days=14),
                closed_at=now - timedelta(days=6),
            )
        )
        await session.commit()
    print(f"seeded {len(FAKE_POSITIONS)} open + 1 closed position for {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
