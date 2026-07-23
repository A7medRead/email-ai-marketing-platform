"""fix campaigns table columns

Revision ID: 52b413cdd105
Revises: 4c4ad978a297
Create Date: 2026-07-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "52b413cdd105"
down_revision: Union[str, Sequence[str], None] = "4c4ad978a297"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "campaigns",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "campaigns",
        sa.Column(
            "body",
            sa.Text(),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE campaigns SET user_id = 1 WHERE user_id IS NULL"
    )

    op.execute(
        "UPDATE campaigns SET body = content WHERE body IS NULL"
    )


def downgrade() -> None:

    op.drop_column(
        "campaigns",
        "body",
    )

    op.drop_column(
        "campaigns",
        "user_id",
    )
