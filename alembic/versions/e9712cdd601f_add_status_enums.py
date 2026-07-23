"""add_status_enums

Revision ID: e9712cdd601f
Revises: 5b2557b000ae
Create Date: 2026-07-23 17:31:40.459892

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e9712cdd601f"
down_revision: Union[str, Sequence[str], None] = "5b2557b000ae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("campaigns") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=30),
            type_=sa.Enum(
                "DRAFT",
                "SCHEDULED",
                "SENDING",
                "COMPLETED",
                "FAILED",
                "CANCELLED",
                name="campaignstatus",
            ),
            existing_nullable=False,
        )


    with op.batch_alter_table("contacts") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=20),
            type_=sa.Enum(
                "ACTIVE",
                "UNSUBSCRIBED",
                "BOUNCED",
                "BLOCKED",
                name="contactstatus",
            ),
            existing_nullable=False,
        )


    with op.batch_alter_table("sender_accounts") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=20),
            type_=sa.Enum(
                "PENDING",
                "VERIFIED",
                "FAILED",
                "DISABLED",
                name="senderaccountstatus",
            ),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("campaigns") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.Enum(
                "DRAFT",
                "SCHEDULED",
                "SENDING",
                "COMPLETED",
                "FAILED",
                "CANCELLED",
                name="campaignstatus",
            ),
            type_=sa.String(length=30),
        )


    with op.batch_alter_table("contacts") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.Enum(
                "ACTIVE",
                "UNSUBSCRIBED",
                "BOUNCED",
                "BLOCKED",
                name="contactstatus",
            ),
            type_=sa.String(length=20),
        )


    with op.batch_alter_table("sender_accounts") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.Enum(
                "PENDING",
                "VERIFIED",
                "FAILED",
                "DISABLED",
                name="senderaccountstatus",
            ),
            type_=sa.String(length=20),
        )
