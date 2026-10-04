"""add batch_size to sender_accounts

Revision ID: a1b2c3d4e5f6
Revises: 8ac54f3bc921
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "8ac54f3bc921"
branch_labels = None
depends_on = None


def upgrade():
    # batch_alter_table: SQLite cannot ALTER many things in place, so Alembic rebuilds the table
    # (this is why env.py disables foreign_keys during migrations).
    with op.batch_alter_table("sender_accounts") as batch:
        batch.add_column(
            sa.Column("batch_size", sa.Integer(), nullable=False, server_default="50")
        )


def downgrade():
    with op.batch_alter_table("sender_accounts") as batch:
        batch.drop_column("batch_size")
