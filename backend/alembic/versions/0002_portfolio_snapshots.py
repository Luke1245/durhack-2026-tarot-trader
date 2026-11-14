"""portfolio snapshots table

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-14

See ADR-0001 amendment: portfolio value history.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Numeric(20, 8), nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_portfolio_snapshots_user_id", "portfolio_snapshots", ["user_id"])
    op.create_index("ix_portfolio_snapshots_taken_at", "portfolio_snapshots", ["taken_at"])


def downgrade() -> None:
    op.drop_index("ix_portfolio_snapshots_taken_at")
    op.drop_index("ix_portfolio_snapshots_user_id")
    op.drop_table("portfolio_snapshots")
