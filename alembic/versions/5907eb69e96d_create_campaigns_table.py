from alembic import op
import sqlalchemy as sa


revision = "5907eb69e96d"
down_revision = "fc2cb24ff638"
branch_labels = None
depends_on = None


def upgrade():

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

    op.drop_table("campaigns")
