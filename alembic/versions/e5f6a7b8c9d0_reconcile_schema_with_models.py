"""reconcile migration-built schema with the current SQLAlchemy models

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9

Databases built by ``alembic upgrade head`` drifted from the ORM models (the long-lived
``emails.db`` was originally built with ``create_all`` and already matches most of this).
Every step is inspector-driven and idempotent, so it is a no-op on a schema that already
matches and never drops data.

Why this exists: the long-lived emails.db was created with create_all, while a database built
only from the migration chain drifted from the models (missing columns, looser NULL rules,
SET NULL instead of CASCADE). Fresh/staging databases therefore broke the ORM. This brings the
chain in line with the models without touching data.

Table rebuilds (SQLAlchemy batch mode, i.e. DROP + CREATE + copy) are used only where SQLite
cannot ALTER NULL/FK rules in place. A rebuild drops the parent table, which with foreign keys
enforced would CASCADE-delete child rows; alembic/env.py therefore forces foreign_keys=OFF for
the migration connection. NULLs are backfilled before any column becomes NOT NULL.

Fixed (needed by, or cheap/safe to align with, the models):
  * contacts.updated_at, templates.subject, templates.body    -- missing columns (ORM errors)
  * campaigns / sender_accounts NOT NULL columns               -- NULLs backfilled first
  * campaigns.sender_account_id / contact_list_id ondelete     -- SET NULL -> CASCADE
  * sender_accounts.user_id ondelete                           -- none -> CASCADE
  * missing indexes declared by the models

Intentionally left alone (see the reconciliation report): campaigns.content,
contacts UNIQUE(user_id, email), and server defaults the models do not declare.
"""
import logging

from alembic import op
import sqlalchemy as sa

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None

log = logging.getLogger("alembic.runtime.migration")

# Lets batch mode name (and so drop/recreate) FKs that SQLite reflects without a name.
NAMING = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}

# (column, backfill value for NULLs)
CAMPAIGN_NOT_NULL = [
    ("body", "''"),
    ("total_recipients", "0"),
    ("sent_count", "0"),
    ("failed_count", "0"),
]
CAMPAIGN_FKS = [
    ("sender_account_id", "sender_accounts"),
    ("contact_list_id", "contact_lists"),
]
SENDER_NOT_NULL = [
    ("provider", "'gmail'"),
    ("status", "'PENDING'"),  # enum member NAME is what SQLAlchemy stores
    ("verified", "0"),
    ("daily_limit", "500"),
    ("hourly_limit", "100"),
    ("daily_sent", "0"),
    ("hourly_sent", "0"),
    ("priority", "1"),
]
INDEXES = [
    ("ix_contacts_email", "contacts", ["email"]),
    ("ix_email_deliveries_campaign_id", "email_deliveries", ["campaign_id"]),
    ("ix_email_deliveries_contact_id", "email_deliveries", ["contact_id"]),
    ("ix_offers_id", "offers", ["id"]),
    ("ix_sender_accounts_user_id", "sender_accounts", ["user_id"]),
]


def _inspector():
    return sa.inspect(op.get_bind())


def _cols(table):
    return {c["name"]: c for c in _inspector().get_columns(table)}


def _fk_for(table, column):
    for fk in _inspector().get_foreign_keys(table):
        if fk["constrained_columns"] == [column]:
            return fk
    return None


def _fk_name(table, column, referred, fk):
    return (fk or {}).get("name") or f"fk_{table}_{column}_{referred}"


def _ondelete(fk):
    return ((fk or {}).get("options") or {}).get("ondelete")


def _has_nulls(table, column):
    return op.get_bind().execute(sa.text(f"SELECT 1 FROM {table} WHERE {column} IS NULL LIMIT 1")).first() is not None


def _backfill(table, column, value):
    op.execute(sa.text(f"UPDATE {table} SET {column} = {value} WHERE {column} IS NULL"))


# --- upgrade ---------------------------------------------------------------------------


def _add_missing_columns():
    if "updated_at" not in _cols("contacts"):
        op.add_column("contacts", sa.Column("updated_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE contacts SET updated_at = created_at WHERE updated_at IS NULL")

    # Pre-existing templates get '' (not NULL); the temporary default is dropped right after.
    templates = _cols("templates")
    added = []
    for name in ("subject", "body"):
        if name not in templates:
            op.add_column("templates", sa.Column(name, sa.String(), nullable=False, server_default=""))
            added.append(name)
    if added:
        with op.batch_alter_table("templates") as batch:
            for name in added:
                batch.alter_column(name, existing_type=sa.String(), existing_nullable=False, server_default=None)


def _reconcile_campaigns():
    cols = _cols("campaigns")

    # `content` is legacy; its data is copied into a NULL body, never dropped.
    if "content" in cols:
        _backfill("campaigns", "body", "COALESCE(content, '')")

    tighten = []
    for name, fill in CAMPAIGN_NOT_NULL:
        if name in cols and cols[name]["nullable"]:
            _backfill("campaigns", name, fill)
            tighten.append(name)

    # Orphaned campaigns (parent already deleted via SET NULL) cannot be made NOT NULL.
    for name, _ in CAMPAIGN_FKS:
        if cols[name]["nullable"]:
            if _has_nulls("campaigns", name):
                log.warning("campaigns.%s has NULL rows; leaving it nullable (needs a data decision)", name)
            else:
                tighten.append(name)

    fk_fixes = []
    for name, referred in CAMPAIGN_FKS:
        fk = _fk_for("campaigns", name)
        if _ondelete(fk) != "CASCADE":
            fk_fixes.append((name, referred, _fk_name("campaigns", name, referred, fk)))

    if not tighten and not fk_fixes:
        return
    with op.batch_alter_table("campaigns", naming_convention=NAMING) as batch:
        for name in tighten:
            batch.alter_column(name, existing_type=cols[name]["type"], nullable=False)
        for name, referred, fk_name in fk_fixes:
            batch.drop_constraint(fk_name, type_="foreignkey")
            batch.create_foreign_key(fk_name, referred, [name], ["id"], ondelete="CASCADE")


def _reconcile_sender_accounts():
    cols = _cols("sender_accounts")
    tighten = []
    for name, fill in SENDER_NOT_NULL:
        if cols[name]["nullable"]:
            _backfill("sender_accounts", name, fill)
            tighten.append(name)

    fk = _fk_for("sender_accounts", "user_id")
    fix_fk = _ondelete(fk) != "CASCADE"

    if not tighten and not fix_fk:
        return
    with op.batch_alter_table("sender_accounts", naming_convention=NAMING) as batch:
        for name in tighten:
            batch.alter_column(name, existing_type=cols[name]["type"], nullable=False)
        if fix_fk:
            fk_name = _fk_name("sender_accounts", "user_id", "users", fk)
            batch.drop_constraint(fk_name, type_="foreignkey")
            batch.create_foreign_key(fk_name, "users", ["user_id"], ["id"], ondelete="CASCADE")


def _create_missing_indexes():
    inspector = _inspector()
    for name, table, columns in INDEXES:
        if name not in {i["name"] for i in inspector.get_indexes(table)}:
            op.create_index(name, table, columns)


def upgrade():
    _add_missing_columns()
    _reconcile_campaigns()
    _reconcile_sender_accounts()
    _create_missing_indexes()


# --- downgrade -------------------------------------------------------------------------
# Restores the d4e5f6a7b8c9 constraints (nullability, ondelete, indexes). The added columns
# are deliberately kept: they may predate this revision (create_all databases) and hold data,
# and an extra column is harmless to the previous revision.


def downgrade():
    for name, table, _ in INDEXES:
        inspector = _inspector()
        if name in {i["name"] for i in inspector.get_indexes(table)}:
            op.drop_index(name, table_name=table)

    cols = _cols("sender_accounts")
    fk = _fk_for("sender_accounts", "user_id")
    loosen = [n for n, _ in SENDER_NOT_NULL if not cols[n]["nullable"]]
    if loosen or _ondelete(fk) == "CASCADE":
        with op.batch_alter_table("sender_accounts", naming_convention=NAMING) as batch:
            for name in loosen:
                batch.alter_column(name, existing_type=cols[name]["type"], nullable=True)
            if _ondelete(fk) == "CASCADE":
                fk_name = _fk_name("sender_accounts", "user_id", "users", fk)
                batch.drop_constraint(fk_name, type_="foreignkey")
                batch.create_foreign_key(fk_name, "users", ["user_id"], ["id"])

    cols = _cols("campaigns")
    loosen = [n for n, _ in CAMPAIGN_NOT_NULL + CAMPAIGN_FKS if not cols[n]["nullable"]]
    fk_fixes = []
    for name, referred in CAMPAIGN_FKS:
        fk = _fk_for("campaigns", name)
        if _ondelete(fk) != "SET NULL":
            fk_fixes.append((name, referred, _fk_name("campaigns", name, referred, fk)))
    if loosen or fk_fixes:
        with op.batch_alter_table("campaigns", naming_convention=NAMING) as batch:
            for name in loosen:
                batch.alter_column(name, existing_type=cols[name]["type"], nullable=True)
            for name, referred, fk_name in fk_fixes:
                batch.drop_constraint(fk_name, type_="foreignkey")
                batch.create_foreign_key(fk_name, referred, [name], ["id"], ondelete="SET NULL")
