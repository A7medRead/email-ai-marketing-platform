"""fix campaign content nullable"""

from alembic import op
import sqlalchemy as sa

revision = "533fec646721"
down_revision = "c99c26ab9dc3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        UPDATE campaigns
        SET content = body
        WHERE content IS NULL
    """)

    with op.batch_alter_table("campaigns") as batch:
        batch.alter_column(
            "content",
            existing_type=sa.Text(),
            nullable=True
        )


def downgrade():
    pass
