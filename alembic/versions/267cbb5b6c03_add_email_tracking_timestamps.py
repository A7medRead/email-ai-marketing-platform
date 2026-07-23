"""add email tracking timestamps

Revision ID: 267cbb5b6c03
Revises: 533fec646721
Create Date: 2026-07-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "267cbb5b6c03"
down_revision: Union[str, Sequence[str], None] = "533fec646721"

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "email_deliveries",
        sa.Column(
            "opened_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "email_deliveries",
        sa.Column(
            "clicked_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:

    op.drop_column(
        "email_deliveries",
        "clicked_at",
    )

    op.drop_column(
        "email_deliveries",
        "opened_at",
    )
