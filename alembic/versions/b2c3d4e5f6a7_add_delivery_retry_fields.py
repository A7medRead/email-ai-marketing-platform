"""add attempt_count, claimed_at, next_attempt_at and CANCELLED to email_deliveries

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

STATUSES = (
    "PENDING",
    "QUEUED",
    "SENDING",
    "SENT",
    "FAILED",
    "OPENED",
    "CLICKED",
    "BOUNCED",
    "CANCELLED",
)


def upgrade():
    # Table rebuild (batch mode) because the status column is widened; see alembic/env.py for why
    # foreign keys are disabled while this runs. Existing rows are copied unchanged.
    with op.batch_alter_table("email_deliveries") as batch:
        batch.add_column(
            sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch.add_column(sa.Column("claimed_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("next_attempt_at", sa.DateTime(), nullable=True))
        # Widen the status column (was VARCHAR(7)) to fit "CANCELLED".
        batch.alter_column(
            "status",
            existing_type=sa.String(length=7),
            type_=sa.Enum(*STATUSES, name="emaildeliverystatus"),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("email_deliveries") as batch:
        batch.drop_column("next_attempt_at")
        batch.drop_column("claimed_at")
        batch.drop_column("attempt_count")
