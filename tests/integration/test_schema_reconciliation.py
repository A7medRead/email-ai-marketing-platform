"""Revision e5f6a7b8c9d0: migration-built schema must match the ORM models.

Every test uses a temporary SQLite file; the real ``emails.db`` is never opened.
"""

import sqlalchemy as sa
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.orm import sessionmaker

import app.features.model_registry  # noqa: F401  (registers all ORM models)
from app.features.contacts.model import Contact
from app.features.templates.model import Template
from app.infrastructure.database import Base
from tests.integration.test_migrations import alembic_config, columns, current_version  # noqa: F401
from tests.integration.test_migrations import cfg, db_path  # noqa: F401  (fixtures)

PREVIOUS = "d4e5f6a7b8c9"
RECONCILE = "e5f6a7b8c9d0"

# Drift deliberately NOT fixed by this revision (documented in the reconciliation report).
LEFT_ALONE = {
    ("remove_column", "campaigns", "content"),
    ("remove_constraint", "contacts", ("user_id", "email")),
}


def classify(diff):
    kind = diff[0]
    if kind == "remove_column":
        return (kind, diff[2], diff[3].name)
    if kind == "remove_constraint":
        c = diff[1]
        return (kind, c.table.name, tuple(col.name for col in c.columns))
    return None


def schema_diffs(engine):
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True})
        return compare_metadata(ctx, Base.metadata)


def unexpected_diffs(engine):
    return [d for d in schema_diffs(engine) if classify(d) not in LEFT_ALONE]


def engine_for(db_path):
    return sa.create_engine(f"sqlite:///{db_path}")


def user_schema(engine):
    with engine.connect() as conn:
        return sorted(conn.execute(sa.text(
            "SELECT name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' AND name != 'alembic_version'"
        )).all())


def semantic_schema(engine):
    insp = sa.inspect(engine)
    out = {}
    for table in sorted(insp.get_table_names()):
        out[table] = (
            sorted((c["name"], str(c["type"]), c["nullable"]) for c in insp.get_columns(table)),
            sorted((tuple(f["constrained_columns"]), f["referred_table"], f["options"].get("ondelete"))
                   for f in insp.get_foreign_keys(table)),
            sorted(i["name"] for i in insp.get_indexes(table)),
        )
    return out


def fk_ondelete(engine, table, column):
    for fk in sa.inspect(engine).get_foreign_keys(table):
        if fk["constrained_columns"] == [column]:
            return fk["options"].get("ondelete")


def index_names(engine, table):
    return {i["name"] for i in sa.inspect(engine).get_indexes(table)}


def test_reconciliation_follows_previous_head_and_is_head(cfg):
    script = ScriptDirectory.from_config(cfg)
    rev = script.get_revision(RECONCILE)
    assert rev.down_revision == PREVIOUS
    assert script.get_heads() == [RECONCILE]


def test_fresh_upgrade_head_matches_models(cfg, db_path):
    command.upgrade(cfg, "head")
    engine = engine_for(db_path)
    assert unexpected_diffs(engine) == []

    insp = sa.inspect(engine)
    assert "updated_at" in columns(insp, "contacts")
    assert {"subject", "body"} <= set(columns(insp, "templates"))
    assert columns(insp, "templates")["subject"]["default"] is None  # temporary '' default dropped

    campaigns = columns(insp, "campaigns")
    for name in ("sender_account_id", "contact_list_id", "body", "total_recipients", "sent_count", "failed_count"):
        assert campaigns[name]["nullable"] is False, name
    sender = columns(insp, "sender_accounts")
    for name in ("provider", "status", "verified", "daily_limit", "hourly_limit", "daily_sent", "hourly_sent", "priority"):
        assert sender[name]["nullable"] is False, name

    assert fk_ondelete(engine, "campaigns", "sender_account_id") == "CASCADE"
    assert fk_ondelete(engine, "campaigns", "contact_list_id") == "CASCADE"
    assert fk_ondelete(engine, "campaigns", "offer_id") == "SET NULL"  # untouched
    assert fk_ondelete(engine, "sender_accounts", "user_id") == "CASCADE"

    assert "ix_contacts_email" in index_names(engine, "contacts")
    assert {"ix_email_deliveries_campaign_id", "ix_email_deliveries_contact_id"} <= index_names(engine, "email_deliveries")
    assert "ix_offers_id" in index_names(engine, "offers")
    assert "ix_sender_accounts_user_id" in index_names(engine, "sender_accounts")
    engine.dispose()


def test_orm_works_on_migrated_database(cfg, db_path):
    """The actual breakage: ORM inserts into contacts/templates on a fresh migrated DB."""
    command.upgrade(cfg, "head")
    engine = engine_for(db_path)
    with engine.begin() as conn:
        conn.execute(sa.text("INSERT INTO users (id, name, email, password) VALUES (1, 'u', 'u@x.io', 'x')"))
    session = sessionmaker(bind=engine)()
    session.add(Contact(user_id=1, first_name="A", email="a@x.io"))
    session.add(Template(user_id=1, name="n", purpose="p", description="d", tone="t", language="en",
                         subject="s", body="b"))
    session.commit()
    assert session.query(Contact).one().updated_at is not None
    assert session.query(Template).one().subject == "s"
    session.close()
    engine.dispose()


def seed_previous_head(conn):
    """Legacy-shaped rows as they exist at d4e5f6a7b8c9 (nullable columns left NULL)."""
    conn.execute(sa.text("INSERT INTO users (id, name, email, password) VALUES (1, 'u', 'u@x.io', 'x')"))
    conn.execute(sa.text("INSERT INTO contact_lists (id, user_id, name, created_at) VALUES (1, 1, 'L', '2026-01-01')"))
    conn.execute(sa.text(
        "INSERT INTO contacts (id, user_id, first_name, email, status, created_at) "
        "VALUES (1, 1, 'A', 'a@x.io', 'ACTIVE', '2026-01-02 03:04:05')"
    ))
    conn.execute(sa.text(
        "INSERT INTO templates (id, user_id, name, purpose, description, tone, language) "
        "VALUES (1, 1, 'tpl', 'p', 'd', 't', 'en')"
    ))
    # Sender with every nullable-in-chain column NULL.
    conn.execute(sa.text("INSERT INTO sender_accounts (id, user_id, name, email, encrypted_password) "
                         "VALUES (1, 1, 'S', 's@x.io', 'enc')"))
    # Healthy campaign, a legacy one (body NULL, content set, NULL counters), and an orphan.
    conn.execute(sa.text(
        "INSERT INTO campaigns (id, user_id, sender_account_id, contact_list_id, name, subject, status, "
        "created_at, body, total_recipients, sent_count, failed_count) "
        "VALUES (1, 1, 1, 1, 'ok', 'subj', 'draft', '2026-01-01', 'hello', 5, 3, 1)"
    ))
    conn.execute(sa.text(
        "INSERT INTO campaigns (id, user_id, sender_account_id, contact_list_id, name, subject, status, "
        "created_at, content) VALUES (2, 1, 1, 1, 'legacy', 'subj', 'draft', '2026-01-01', 'legacy body')"
    ))


def assert_seed_preserved(engine, orphan_nullable=None):
    with engine.connect() as conn:
        q = lambda sql: conn.execute(sa.text(sql)).all()  # noqa: E731
        assert q("SELECT id, email, first_name FROM contacts") == [(1, "a@x.io", "A")]
        assert q("SELECT id, name, purpose FROM templates") == [(1, "tpl", "p")]
        assert q("SELECT id, name, encrypted_password FROM sender_accounts") == [(1, "S", "enc")]
        assert q("SELECT id, name, body, total_recipients, sent_count, failed_count FROM campaigns ORDER BY id") == [
            (1, "ok", "hello", 5, 3, 1),
            (2, "legacy", "legacy body", 0, 0, 0),  # body recovered from content, counters 0
        ]
        assert q("SELECT content FROM campaigns WHERE id = 2") == [("legacy body",)]  # content never dropped
        assert q("SELECT provider, status, verified, daily_limit, hourly_limit, daily_sent, hourly_sent, priority "
                 "FROM sender_accounts") == [("gmail", "PENDING", 0, 500, 100, 0, 0, 1)]
        assert q("SELECT subject, body FROM templates") == [("", "")]
        assert q("SELECT updated_at FROM contacts") == [("2026-01-02 03:04:05",)]


def test_existing_data_survives_upgrade_downgrade_upgrade(cfg, db_path):
    command.upgrade(cfg, PREVIOUS)
    engine = engine_for(db_path)
    with engine.begin() as conn:
        seed_previous_head(conn)

    command.upgrade(cfg, "head")
    assert_seed_preserved(engine)
    assert unexpected_diffs(engine) == []

    command.downgrade(cfg, PREVIOUS)
    assert current_version(engine) == PREVIOUS
    insp = sa.inspect(engine)
    assert columns(insp, "campaigns")["body"]["nullable"] is True
    assert columns(insp, "sender_accounts")["provider"]["nullable"] is True
    assert fk_ondelete(engine, "campaigns", "sender_account_id") == "SET NULL"
    assert "ix_contacts_email" not in index_names(engine, "contacts")
    assert_seed_preserved(engine)  # downgrade is non-destructive

    command.upgrade(cfg, "head")
    assert current_version(engine) == RECONCILE
    assert_seed_preserved(engine)
    assert unexpected_diffs(engine) == []
    engine.dispose()


def test_orphan_campaigns_stay_nullable_and_are_not_deleted(cfg, db_path):
    command.upgrade(cfg, PREVIOUS)
    engine = engine_for(db_path)
    with engine.begin() as conn:
        seed_previous_head(conn)
        conn.execute(sa.text(
            "INSERT INTO campaigns (id, user_id, sender_account_id, contact_list_id, name, subject, status, "
            "created_at, body) VALUES (3, 1, NULL, 1, 'orphan', 's', 'draft', '2026-01-01', 'b')"
        ))
    command.upgrade(cfg, "head")
    insp = sa.inspect(engine)
    assert columns(insp, "campaigns")["sender_account_id"]["nullable"] is True  # data decision needed
    assert columns(insp, "campaigns")["contact_list_id"]["nullable"] is False
    with engine.connect() as conn:
        assert conn.execute(sa.text("SELECT COUNT(*) FROM campaigns")).scalar() == 3
    engine.dispose()


def test_upgrade_is_idempotent_on_create_all_database(cfg, db_path):
    """The real emails.db was built by create_all: the migration must be a no-op there."""
    engine = engine_for(db_path)
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(sa.text("INSERT INTO users (id, name, email, password) VALUES (1, 'u', 'u@x.io', 'x')"))
        conn.execute(sa.text(
            "INSERT INTO contacts (id, user_id, first_name, email, status, created_at, updated_at) "
            "VALUES (1, 1, 'A', 'a@x.io', 'ACTIVE', '2026-01-02', '2026-02-03')"
        ))
        conn.execute(sa.text(
            "INSERT INTO templates (id, user_id, name, purpose, description, tone, language, subject, body) "
            "VALUES (1, 1, 'tpl', 'p', 'd', 't', 'en', 'real subject', 'real body')"
        ))
    schema_before = user_schema(engine)
    command.stamp(cfg, PREVIOUS)

    command.upgrade(cfg, "head")

    with engine.connect() as conn:
        assert conn.execute(sa.text("SELECT updated_at FROM contacts")).scalar() == "2026-02-03"  # not overwritten
        assert conn.execute(sa.text("SELECT subject, body FROM templates")).all() == [("real subject", "real body")]
    assert user_schema(engine) == schema_before  # byte-identical DDL: nothing was rebuilt
    assert unexpected_diffs(engine) == []
    engine.dispose()


def test_running_upgrade_twice_via_downgrade_is_stable(cfg, db_path):
    command.upgrade(cfg, "head")
    engine = engine_for(db_path)
    first = semantic_schema(engine)
    command.downgrade(cfg, PREVIOUS)
    command.upgrade(cfg, "head")
    assert semantic_schema(engine) == first
    assert unexpected_diffs(engine) == []
    engine.dispose()


# --- LOCKED decision: CASCADE is the intended delete behaviour ------------------------------


def fk_on_engine(db_path):
    """Engine on a migration-built DB with SQLite FK enforcement on (it is off by default)."""
    engine = engine_for(db_path)

    @sa.event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    return engine


def seed_cascade_graph(conn):
    conn.execute(sa.text("INSERT INTO users (id, name, email, password) VALUES (1, 'u', 'u@x.io', 'x')"))
    conn.execute(sa.text("INSERT INTO contact_lists (id, user_id, name, created_at) VALUES (1, 1, 'L', '2026-01-01')"))
    conn.execute(sa.text("INSERT INTO contact_lists (id, user_id, name, created_at) VALUES (2, 1, 'L2', '2026-01-01')"))
    for sid in (1, 2):
        conn.execute(sa.text(
            "INSERT INTO sender_accounts (id, user_id, name, email, encrypted_password, provider, status, verified, "
            "daily_limit, hourly_limit, daily_sent, hourly_sent, priority) "
            f"VALUES ({sid}, 1, 'S', 's{sid}@x.io', 'enc', 'gmail', 'PENDING', 0, 1, 1, 0, 0, 1)"
        ))
    conn.execute(sa.text(
        "INSERT INTO contacts (id, user_id, first_name, email, status, created_at) "
        "VALUES (1, 1, 'A', 'a@x.io', 'ACTIVE', '2026-01-01')"
    ))
    for cid, sid, lid in ((1, 1, 1), (2, 2, 1), (3, 2, 2)):
        conn.execute(sa.text(
            "INSERT INTO campaigns (id, user_id, sender_account_id, contact_list_id, name, subject, status, "
            "created_at, body, total_recipients, sent_count, failed_count) "
            f"VALUES ({cid}, 1, {sid}, {lid}, 'c{cid}', 's', 'draft', '2026-01-01', 'b', 0, 0, 0)"
        ))
        conn.execute(sa.text(
            "INSERT INTO email_deliveries (campaign_id, contact_id, recipient_email, status, created_at) "
            f"VALUES ({cid}, 1, 'a@x.io', 'PENDING', '2026-01-01')"
        ))


def ids(conn, table):
    return [r[0] for r in conn.execute(sa.text(f"SELECT id FROM {table} ORDER BY id"))]


def test_cascade_deleting_sender_account_deletes_its_campaigns(cfg, db_path):
    command.upgrade(cfg, "head")
    engine = fk_on_engine(db_path)
    with engine.begin() as conn:
        seed_cascade_graph(conn)
        conn.execute(sa.text("DELETE FROM sender_accounts WHERE id = 2"))
        assert ids(conn, "campaigns") == [1]  # campaigns 2 and 3 cascaded
        assert ids(conn, "contact_lists") == [1, 2]  # nothing else touched
        assert conn.execute(sa.text("SELECT COUNT(*) FROM email_deliveries")).scalar() == 1  # their deliveries too
    engine.dispose()


def test_cascade_deleting_contact_list_deletes_its_campaigns(cfg, db_path):
    command.upgrade(cfg, "head")
    engine = fk_on_engine(db_path)
    with engine.begin() as conn:
        seed_cascade_graph(conn)
        conn.execute(sa.text("DELETE FROM contact_lists WHERE id = 1"))
        assert ids(conn, "campaigns") == [3]  # campaigns 1 and 2 cascaded
        assert ids(conn, "sender_accounts") == [1, 2]
    engine.dispose()


def test_cascade_deleting_user_deletes_sender_accounts(cfg, db_path):
    command.upgrade(cfg, "head")
    engine = fk_on_engine(db_path)
    with engine.begin() as conn:
        seed_cascade_graph(conn)
        conn.execute(sa.text("DELETE FROM users WHERE id = 1"))
        assert ids(conn, "sender_accounts") == []
        assert ids(conn, "campaigns") == []
    engine.dispose()


def test_cascade_still_holds_after_downgrade_upgrade_round_trip(cfg, db_path):
    command.upgrade(cfg, "head")
    command.downgrade(cfg, PREVIOUS)
    command.upgrade(cfg, "head")
    engine = fk_on_engine(db_path)
    with engine.begin() as conn:
        seed_cascade_graph(conn)
        conn.execute(sa.text("DELETE FROM sender_accounts WHERE id = 1"))
        assert ids(conn, "campaigns") == [2, 3]
    engine.dispose()
