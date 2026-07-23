"""add missing campaign counters

Revision ID: c99c26ab9dc3
Revises: 52b413cdd105
Create Date: 2026-07-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c99c26ab9dc3"
down_revision: Union[str, Sequence[str], None] = "52b413cdd105"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "campaigns",
        sa.Column(
            "total_recipients",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),
    )

    op.add_column(
        "campaigns",
        sa.Column(
            "sent_count",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),
    )

    op.add_column(
        "campaigns",
        sa.Column(
            "failed_count",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),
    )

    op.add_column(
        "campaigns",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:

    op.drop_column("campaigns", "updated_at")
    op.drop_column("campaigns", "failed_count")
    op.drop_column("campaigns", "sent_count")
    op.drop_column("campaigns", "total_recipients")
