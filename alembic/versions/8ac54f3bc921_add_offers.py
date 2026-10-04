"""add reusable offers and campaign association

Revision ID: 8ac54f3bc921
Revises: 436cdefb599b
"""
from alembic import op
import sqlalchemy as sa

revision = "8ac54f3bc921"
down_revision = "436cdefb599b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("discount", sa.String(80), nullable=True),
        sa.Column("coupon_code", sa.String(80), nullable=True),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("cta_label", sa.String(80), nullable=True),
        sa.Column("cta_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_offers_user_id", "offers", ["user_id"])
    with op.batch_alter_table("campaigns") as batch:
        batch.add_column(sa.Column("offer_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_campaigns_offer_id_offers", "offers", ["offer_id"], ["id"], ondelete="SET NULL")


def downgrade():
    with op.batch_alter_table("campaigns") as batch:
        batch.drop_constraint("fk_campaigns_offer_id_offers", type_="foreignkey")
        batch.drop_column("offer_id")
    op.drop_index("ix_offers_user_id", table_name="offers")
    op.drop_table("offers")
