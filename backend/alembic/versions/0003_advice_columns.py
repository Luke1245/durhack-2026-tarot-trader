"""advice columns on readings

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-14

Gemini advice lane: the Advice (side + asset) lives on the reading;
per-card narratives (price-action mapping) on reading_cards.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("readings") as batch:
        batch.add_column(sa.Column("side", sa.String(5), nullable=True))
        batch.add_column(
            sa.Column(
                "asset_id",
                sa.Integer(),
                sa.ForeignKey("assets.id", name="fk_readings_asset_id"),
                nullable=True,
            )
        )
        batch.create_index("ix_readings_asset_id", ["asset_id"])
    with op.batch_alter_table("reading_cards") as batch:
        batch.add_column(sa.Column("narrative", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("readings") as batch:
        batch.drop_index("ix_readings_asset_id")
        batch.drop_column("asset_id")
        batch.drop_column("side")
    with op.batch_alter_table("reading_cards") as batch:
        batch.drop_column("narrative")
