"""news event columns on readings

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-14

The news event that motivated the asset pick (headline + url, nullable
when the pick was event-less).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("readings") as batch:
        batch.add_column(sa.Column("event_headline", sa.Text(), nullable=True))
        batch.add_column(sa.Column("event_url", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("readings") as batch:
        batch.drop_column("event_url")
        batch.drop_column("event_headline")
