from alembic import op
import sqlalchemy as sa


revision = "5907eb69e96d"
down_revision = "fc2cb24ff638"
branch_labels = None
depends_on = None


def upgrade():

    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("campaigns"):
        # History fix: this revision originally created `campaigns` unconditionally, which fails on
        # any DB that already has it (the initial schema 21ff1ae415e1 creates it, and the long-lived
        # production DB was built with create_all). It was edited, not replaced, so revision IDs
        # and the chain stay intact. Already-applied databases never re-run it. Only the legacy
        # `content` column that the following migrations read from is added.
        columns = {c["name"] for c in inspector.get_columns("campaigns")}
        if "content" not in columns:
            op.add_column("campaigns", sa.Column("content", sa.Text(), nullable=True))
        return

    op.create_table(
        "campaigns",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "sender_account_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "contact_list_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "subject",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "content",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "scheduled_at",
            sa.DateTime(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["sender_account_id"],
            ["sender_accounts.id"],
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["contact_list_id"],
            ["contact_lists.id"],
            ondelete="CASCADE"
        ),
    )


def downgrade():

    # `campaigns` is owned by the initial schema; dropping it here would break the
    # downgrade of 21ff1ae415e1. Only remove the `content` column this revision may add.
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("campaigns") and "content" in {
        c["name"] for c in inspector.get_columns("campaigns")
    }:
        with op.batch_alter_table("campaigns") as batch:
            batch.drop_column("content")
