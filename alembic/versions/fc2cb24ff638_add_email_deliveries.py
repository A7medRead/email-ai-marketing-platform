"""add_email_deliveries

Revision ID: fc2cb24ff638
Revises: e9712cdd601f
Create Date: 2026-07-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fc2cb24ff638"
down_revision: Union[str, Sequence[str], None] = "e9712cdd601f"

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "email_deliveries",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "campaign_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "contact_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "sender_account_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "recipient_email",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "QUEUED",
                "SENT",
                "FAILED",
                "OPENED",
                "CLICKED",
                "BOUNCED",
                name="emaildeliverystatus",
            ),
            nullable=False,
        ),

        sa.Column(
            "error_message",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "sent_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaigns.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["contacts.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["sender_account_id"],
            ["sender_accounts.id"],
            ondelete="SET NULL",
        ),
    )


def downgrade() -> None:

    op.drop_table(
        "email_deliveries"
    )
