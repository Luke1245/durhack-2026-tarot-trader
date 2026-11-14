"""add finnhub_symbol to assets (crypto quotes)

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-14

Crypto trades on Finnhub under symbols like BINANCE:BTCUSDT; stocks use
their plain ticker. finnhub_symbol holds the provider symbol when it
differs from the display symbol; NULL means "use symbol" (all stocks).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("assets") as batch:
        batch.add_column(sa.Column("finnhub_symbol", sa.String(40), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("assets") as batch:
        batch.drop_column("finnhub_symbol")
