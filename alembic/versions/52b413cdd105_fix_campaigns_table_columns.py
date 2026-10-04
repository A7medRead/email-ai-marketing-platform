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

    # History fix: `user_id` already exists in the initial schema and databases built with
    # create_all already have `body`; blindly adding them failed with "duplicate column".
    # Inspecting first makes this safe on both fresh and long-lived databases.
    columns = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("campaigns")}

    if "user_id" not in columns:
        op.add_column(
            "campaigns",
            sa.Column(
                "user_id",
                sa.Integer(),
                nullable=True,
            ),
        )

    if "body" not in columns:
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

    # `user_id` is part of the initial schema (21ff1ae415e1) and is intentionally kept.
