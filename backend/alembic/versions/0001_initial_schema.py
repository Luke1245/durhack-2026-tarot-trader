"""initial schema: users, sessions, tarot_cards, readings, reading_cards, assets, positions

Revision ID: 0001
Revises:
Create Date: 2026-11-14

Replaces the scaffold's provisional `readings` table (JSONB card blob).
Fresh databases only; existing dev databases should be recreated.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The scaffold created a provisional `readings` table via create_all; drop it
    # so this migration can upgrade existing dev databases, not just fresh ones.
    op.execute("DROP TABLE IF EXISTS readings")
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "tarot_cards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("arcana", sa.String(10), nullable=False),
        sa.Column("suit", sa.String(20), nullable=True),
        sa.Column("rank", sa.String(20), nullable=True),
        sa.Column("upright", sa.Text(), nullable=False),
        sa.Column("reversed", sa.Text(), nullable=False),
        sa.Column("love", sa.Text(), nullable=False),
        sa.Column("career", sa.Text(), nullable=False),
        sa.Column("yes_no", sa.String(20), nullable=False),
        sa.Column("element", sa.String(20), nullable=True),
        sa.Column("zodiac", sa.String(50), nullable=True),
        sa.Column("guide_url", sa.Text(), nullable=True),
        sa.Column("image_path", sa.Text(), nullable=True),
    )

    op.create_table(
        "readings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("interpretation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "reading_cards",
        sa.Column("reading_id", sa.Uuid(), sa.ForeignKey("readings.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("tarot_cards.id"), primary_key=True),
        sa.Column("position", sa.String(10), nullable=False),
        sa.Column("reversed", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
    )

    op.create_table(
        "positions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("reading_id", sa.Uuid(), sa.ForeignKey("readings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("side", sa.String(5), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("entry_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("status", sa.String(10), nullable=False, server_default="open"),
        sa.Column("exit_price", sa.Numeric(20, 8), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Enum domains (side/status/position/arcana) are enforced at the
    # Pydantic/service layer, not via DB check constraints, to keep
    # migrations portable across SQLite (tests) and Postgres (production).

    # Postgres does not auto-index foreign keys.
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_readings_user_id", "readings", ["user_id"])
    op.create_index("ix_reading_cards_card_id", "reading_cards", ["card_id"])
    op.create_index("ix_positions_user_id", "positions", ["user_id"])
    op.create_index("ix_positions_asset_id", "positions", ["asset_id"])
    op.create_index("ix_positions_reading_id", "positions", ["reading_id"])


def downgrade() -> None:
    for index in (
        "ix_positions_reading_id",
        "ix_positions_asset_id",
        "ix_positions_user_id",
        "ix_reading_cards_card_id",
        "ix_readings_user_id",
        "ix_sessions_user_id",
    ):
        op.drop_index(index)
    for table in ("positions", "assets", "reading_cards", "readings", "tarot_cards", "sessions", "users"):
        op.drop_table(table)
