"""add responders, offer ownership, affiliate_url, offer_variants and campaigns.variant_id

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None

CONTENT_TYPES = ("TEXT", "IMAGE", "TEXT_IMAGE", "HTML")


def upgrade():
    op.create_table(
        "responders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_responders_id", "responders", ["id"])
    op.create_index("ix_responders_user_id", "responders", ["user_id"])

    # Rebuilds `offers` (batch mode) to add the FK; safe because env.py disables foreign_keys.
    # responder_id stays nullable so pre-Responder offers keep working (backfilled below).
    with op.batch_alter_table("offers") as batch:
        batch.add_column(sa.Column("responder_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("affiliate_url", sa.String(2048), nullable=True))
        batch.create_foreign_key(
            "fk_offers_responder_id_responders", "responders", ["responder_id"], ["id"], ondelete="RESTRICT"
        )
        batch.create_index("ix_offers_responder_id", ["responder_id"])

    op.create_table(
        "offer_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("content_type", sa.Enum(*CONTENT_TYPES, name="variantcontenttype"), nullable=False),
        sa.Column("from_name", sa.String(255), nullable=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_offer_variants_id", "offer_variants", ["id"])
    op.create_index("ix_offer_variants_offer_id", "offer_variants", ["offer_id"])

    with op.batch_alter_table("campaigns") as batch:
        batch.add_column(sa.Column("variant_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_campaigns_variant_id_offer_variants", "offer_variants", ["variant_id"], ["id"], ondelete="SET NULL"
        )
        batch.create_index("ix_campaigns_variant_id", ["variant_id"])

    backfill_default_responders(op.get_bind())


def backfill_default_responders(conn):
    """Give every user without a Responder a Default Responder; attach their unassigned offers to it."""
    conn.execute(
        sa.text(
            "INSERT INTO responders (user_id, name, created_at) "
            "SELECT id, 'Default Responder', :now FROM users "
            "WHERE id NOT IN (SELECT user_id FROM responders)"
        ),
        {"now": datetime.utcnow()},
    )
    conn.execute(
        sa.text(
            "UPDATE offers SET responder_id = "
            "(SELECT MIN(r.id) FROM responders r WHERE r.user_id = offers.user_id) "
            "WHERE responder_id IS NULL "
            "AND EXISTS (SELECT 1 FROM responders r WHERE r.user_id = offers.user_id)"
        )
    )


def downgrade():
    with op.batch_alter_table("campaigns") as batch:
        batch.drop_index("ix_campaigns_variant_id")
        batch.drop_constraint("fk_campaigns_variant_id_offer_variants", type_="foreignkey")
        batch.drop_column("variant_id")
    op.drop_index("ix_offer_variants_offer_id", table_name="offer_variants")
    op.drop_index("ix_offer_variants_id", table_name="offer_variants")
    op.drop_table("offer_variants")
    with op.batch_alter_table("offers") as batch:
        batch.drop_index("ix_offers_responder_id")
        batch.drop_constraint("fk_offers_responder_id_responders", type_="foreignkey")
        batch.drop_column("affiliate_url")
        batch.drop_column("responder_id")
    op.drop_index("ix_responders_user_id", table_name="responders")
    op.drop_index("ix_responders_id", table_name="responders")
    op.drop_table("responders")
