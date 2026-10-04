"""add campaigns.prepared_subject, prepared_from_name, prepared_body (Variant snapshot)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
"""
from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    # All nullable: legacy campaigns have no snapshot and keep using subject/body/from_name.
    with op.batch_alter_table("campaigns") as batch:
        batch.add_column(sa.Column("prepared_subject", sa.String(255), nullable=True))
        batch.add_column(sa.Column("prepared_from_name", sa.String(255), nullable=True))
        batch.add_column(sa.Column("prepared_body", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("campaigns") as batch:
        batch.drop_column("prepared_body")
        batch.drop_column("prepared_from_name")
        batch.drop_column("prepared_subject")
