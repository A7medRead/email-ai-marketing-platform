"""Alembic migration chain: fresh build, round trip, and the Default Responder backfill.

Every test uses a temporary SQLite file; the real ``emails.db`` is never opened.
"""

import importlib.util
from datetime import datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = ROOT / "alembic" / "versions"

BEFORE_RESPONDERS = "b2c3d4e5f6a7"
RESPONDERS = "c3d4e5f6a7b8"

EXPECTED_TABLES = {
    "users",
    "contact_lists",
    "contacts",
    "contact_list_contacts",
    "emails",
    "templates",
    "sender_accounts",
    "campaigns",
    "email_deliveries",
    "offers",
    "responders",
    "offer_variants",
}


def alembic_config(db_path) -> Config:
    # No ini file: env.py then skips fileConfig() and leaves test logging untouched.
    cfg = Config()
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "migration.db"


@pytest.fixture
def cfg(db_path):
    return alembic_config(db_path)


@pytest.fixture
def inspect_db(db_path):
    def _inspect():
        engine = sa.create_engine(f"sqlite:///{db_path}")
        return engine, sa.inspect(engine)

    return _inspect


def columns(inspector, table):
    return {c["name"]: c for c in inspector.get_columns(table)}


def current_version(engine):
    with engine.connect() as conn:
        return conn.execute(sa.text("SELECT version_num FROM alembic_version")).scalar()


def assert_head_schema(engine, inspector):
    assert EXPECTED_TABLES <= set(inspector.get_table_names())

    offers = columns(inspector, "offers")
    assert {"responder_id", "affiliate_url", "user_id"} <= set(offers)
    assert offers["responder_id"]["nullable"] is True
    assert {fk["referred_table"] for fk in inspector.get_foreign_keys("offers")} == {
        "users",
        "responders",
    }

    assert {"id", "user_id", "name", "created_at"} <= set(columns(inspector, "responders"))
    assert {fk["referred_table"] for fk in inspector.get_foreign_keys("responders")} == {"users"}

    variants = columns(inspector, "offer_variants")
    assert {
        "offer_id",
        "name",
        "content_type",
        "from_name",
        "subject",
        "body_html",
        "body_text",
        "image_url",
        "is_active",
    } <= set(variants)
    assert {fk["referred_table"] for fk in inspector.get_foreign_keys("offer_variants")} == {"offers"}

    campaigns = columns(inspector, "campaigns")
    assert {"prepared_subject", "prepared_from_name", "prepared_body"} <= set(campaigns)
    assert {"offer_id", "variant_id", "from_name", "body"} <= set(campaigns)
    assert all(campaigns[c]["nullable"] for c in ("prepared_subject", "prepared_from_name", "prepared_body"))

    assert "batch_size" in columns(inspector, "sender_accounts")

    deliveries = columns(inspector, "email_deliveries")
    assert {"attempt_count", "claimed_at", "next_attempt_at", "opened_at", "clicked_at"} <= set(deliveries)


def test_chain_is_linear_with_single_root_and_head(cfg):
    script = ScriptDirectory.from_config(cfg)
    assert len(script.get_heads()) == 1
    assert len(script.get_bases()) == 1
    revisions = list(script.walk_revisions())
    assert len(revisions) == len(list(VERSIONS_DIR.glob("*.py")))
    assert all(len(rev.nextrev) <= 1 for rev in revisions)


def test_fresh_database_upgrade_downgrade_upgrade(cfg, db_path, inspect_db):
    head = ScriptDirectory.from_config(cfg).get_current_head()

    command.upgrade(cfg, "head")
    engine, inspector = inspect_db()
    assert current_version(engine) == head
    assert_head_schema(engine, inspector)
    engine.dispose()

    command.downgrade(cfg, "base")
    engine, inspector = inspect_db()
    assert set(inspector.get_table_names()) == {"alembic_version"}
    engine.dispose()

    command.upgrade(cfg, "head")
    engine, inspector = inspect_db()
    assert current_version(engine) == head
    assert_head_schema(engine, inspector)
    engine.dispose()


# --- Default Responder backfill -------------------------------------------------------


NOW = datetime(2026, 1, 1)


def add_user(conn, email):
    return conn.execute(
        sa.text("INSERT INTO users (name, email, password) VALUES (:n, :e, 'x') RETURNING id"),
        {"n": email, "e": email},
    ).scalar()


def add_offer(conn, user_id, name, responder_id=None):
    params = {"u": user_id, "n": name, "now": NOW}
    if responder_id is None:
        sql = (
            "INSERT INTO offers (user_id, name, title, description, created_at, updated_at) "
            "VALUES (:u, :n, :n, 'd', :now, :now) RETURNING id"
        )
    else:
        sql = (
            "INSERT INTO offers (user_id, name, title, description, created_at, updated_at, responder_id) "
            "VALUES (:u, :n, :n, 'd', :now, :now, :r) RETURNING id"
        )
        params["r"] = responder_id
    return conn.execute(sa.text(sql), params).scalar()


def add_responder(conn, user_id, name):
    return conn.execute(
        sa.text("INSERT INTO responders (user_id, name, created_at) VALUES (:u, :n, :now) RETURNING id"),
        {"u": user_id, "n": name, "now": NOW},
    ).scalar()


def ownership_violations(conn):
    return conn.execute(
        sa.text(
            "SELECT COUNT(*) FROM offers o JOIN responders r ON r.id = o.responder_id "
            "WHERE o.user_id != r.user_id"
        )
    ).scalar()


def test_migration_backfills_default_responder_per_user(cfg, db_path):
    command.upgrade(cfg, BEFORE_RESPONDERS)
    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        alice = add_user(conn, "alice@example.com")
        bob = add_user(conn, "bob@example.com")
        carol = add_user(conn, "carol@example.com")  # no offers at all
        alice_offers = [add_offer(conn, alice, "a1"), add_offer(conn, alice, "a2")]
        bob_offers = [add_offer(conn, bob, "b1")]

    command.upgrade(cfg, "head")

    with engine.connect() as conn:
        responders = conn.execute(sa.text("SELECT id, user_id, name FROM responders")).all()
        by_user = {}
        for rid, uid, name in responders:
            by_user.setdefault(uid, []).append((rid, name))

        # Exactly one Default Responder per user; none shared between users.
        assert sorted(by_user) == [alice, bob, carol]
        assert all(len(v) == 1 and v[0][1] == "Default Responder" for v in by_user.values())

        owner = dict(conn.execute(sa.text("SELECT id, responder_id FROM offers")).all())
        assert all(owner[o] == by_user[alice][0][0] for o in alice_offers)
        assert all(owner[o] == by_user[bob][0][0] for o in bob_offers)
        assert ownership_violations(conn) == 0
        assert conn.execute(sa.text("SELECT COUNT(*) FROM offers WHERE responder_id IS NULL")).scalar() == 0
    engine.dispose()


@pytest.fixture
def backfill():
    spec = importlib.util.spec_from_file_location(
        "responders_migration", VERSIONS_DIR / "c3d4e5f6a7b8_add_responders_and_offer_variants.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.backfill_default_responders


def test_backfill_reuses_existing_responder_and_is_scoped_to_user(cfg, db_path, backfill):
    command.upgrade(cfg, "head")
    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        alice = add_user(conn, "alice@example.com")
        bob = add_user(conn, "bob@example.com")
        # Alice already has a Responder (and an unassigned legacy offer); Bob has none.
        alice_responder = add_responder(conn, alice, "Alice's own")
        legacy_alice = add_offer(conn, alice, "legacy-a")
        legacy_bob = add_offer(conn, bob, "legacy-b")

        backfill(conn)

        responders = conn.execute(sa.text("SELECT id, user_id FROM responders")).all()
        bob_responders = [rid for rid, uid in responders if uid == bob]
        assert len([1 for _, uid in responders if uid == alice]) == 1  # no extra for Alice
        assert len(bob_responders) == 1

        owner = dict(conn.execute(sa.text("SELECT id, responder_id FROM offers")).all())
        assert owner[legacy_alice] == alice_responder
        assert owner[legacy_bob] == bob_responders[0]
        assert ownership_violations(conn) == 0
    engine.dispose()


def test_backfill_with_multiple_responders_picks_same_user_only(cfg, db_path, backfill):
    command.upgrade(cfg, "head")
    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        alice = add_user(conn, "alice@example.com")
        bob = add_user(conn, "bob@example.com")
        bob_responder = add_responder(conn, bob, "Bob first")  # lowest id overall, but not Alice's
        alice_first = add_responder(conn, alice, "Alice first")
        alice_second = add_responder(conn, alice, "Alice second")
        legacy = add_offer(conn, alice, "legacy-a")
        assigned = add_offer(conn, alice, "assigned-a", responder_id=alice_second)

        backfill(conn)

        owner = dict(conn.execute(sa.text("SELECT id, responder_id FROM offers")).all())
        assert owner[legacy] == alice_first  # deterministic: lowest id of the SAME user
        assert owner[legacy] != bob_responder
        assert owner[assigned] == alice_second  # already-assigned offers are never reassigned
        assert conn.execute(sa.text("SELECT COUNT(*) FROM responders WHERE user_id = :u"), {"u": alice}).scalar() == 2
        assert ownership_violations(conn) == 0
    engine.dispose()


def test_backfill_is_idempotent(cfg, db_path, backfill):
    command.upgrade(cfg, "head")
    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        user = add_user(conn, "alice@example.com")
        add_offer(conn, user, "legacy")
        backfill(conn)
        snapshot = conn.execute(sa.text("SELECT id, user_id FROM responders ORDER BY id")).all()
        offers = conn.execute(sa.text("SELECT id, responder_id FROM offers ORDER BY id")).all()
        backfill(conn)
        assert conn.execute(sa.text("SELECT id, user_id FROM responders ORDER BY id")).all() == snapshot
        assert conn.execute(sa.text("SELECT id, responder_id FROM offers ORDER BY id")).all() == offers
    engine.dispose()


# --- foreign_keys guard (alembic/env.py) ------------------------------------------------
#
# Production recovery policy: if a production migration fails, recovery is by restoring the
# pre-migration BACKUP of emails.db. `alembic downgrade` is never the recovery plan.
#
# SQLite batch migrations rebuild tables with DROP/CREATE. If foreign_keys were ON, dropping
# a parent table would fire ON DELETE CASCADE and silently delete child rows. env.py therefore
# forces PRAGMA foreign_keys=OFF on the connection Alembic migrates through. Application
# runtime connections are deliberately NOT changed (FK enforcement there is a separate decision).

PRE_RECONCILE = "436cdefb599b"
RECONCILE = "e5f6a7b8c9d0"


@pytest.fixture
def hostile_fk_on():
    """Make every new SQLite connection start with foreign_keys=ON (worst case for a rebuild).

    Registered at Engine-class level, so it runs before the instance-level guard in env.py;
    only the guard can turn enforcement back off.
    """
    from sqlalchemy.engine import Engine

    def enable(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    sa.event.listen(Engine, "connect", enable)
    yield
    sa.event.remove(Engine, "connect", enable)


def test_hostile_fixture_really_enables_foreign_keys(db_path, hostile_fk_on):
    # Control: proves the guard tests below are not vacuous.
    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        assert conn.execute(sa.text("PRAGMA foreign_keys")).scalar() == 1
    engine.dispose()


def test_migrations_run_with_foreign_keys_disabled(cfg, db_path, hostile_fk_on):
    from sqlalchemy.engine import Engine

    command.upgrade(cfg, PRE_RECONCILE)

    seen = []  # (statement kind, foreign_keys pragma value) for every table rebuild step

    def record(conn, cursor, statement, parameters, context, executemany):
        kind = statement.lstrip().upper()[:11]
        if kind.startswith(("DROP TABLE", "CREATE TABLE", "ALTER TABLE")):
            seen.append((kind, cursor.connection.execute("PRAGMA foreign_keys").fetchone()[0]))

    sa.event.listen(Engine, "before_cursor_execute", record)
    try:
        command.upgrade(cfg, RECONCILE)
    finally:
        sa.event.remove(Engine, "before_cursor_execute", record)

    assert any(kind.startswith("DROP TABLE") for kind, _ in seen), "expected table rebuilds"
    assert all(fk == 0 for _, fk in seen), seen


def test_pre_reconcile_to_reconcile_keeps_all_rows_even_with_fk_enforcement_default_on(cfg, db_path, hostile_fk_on):
    command.upgrade(cfg, PRE_RECONCILE)
    engine = sa.create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        conn.execute(sa.text("PRAGMA foreign_keys=OFF"))  # seed in any order
        user = conn.execute(
            sa.text("INSERT INTO users (name, email, password) VALUES ('u', 'u@example.com', 'x') RETURNING id")
        ).scalar()
        lst = conn.execute(
            sa.text("INSERT INTO contact_lists (user_id, name, created_at) VALUES (:u, 'l', :now) RETURNING id"),
            {"u": user, "now": NOW},
        ).scalar()
        contact = conn.execute(
            sa.text(
                "INSERT INTO contacts (user_id, first_name, email, status, created_at) "
                "VALUES (:u, 'c', 'c@example.com', 'ACTIVE', :now) RETURNING id"
            ),
            {"u": user, "now": NOW},
        ).scalar()
        conn.execute(
            sa.text("INSERT INTO contact_list_contacts (contact_list_id, contact_id) VALUES (:l, :c)"),
            {"l": lst, "c": contact},
        )
        sender = conn.execute(
            sa.text(
                "INSERT INTO sender_accounts (user_id, name, email, encrypted_password) "
                "VALUES (:u, 's', 's@example.com', 'x') RETURNING id"
            ),
            {"u": user},
        ).scalar()
        conn.execute(
            sa.text(
                "INSERT INTO campaigns (user_id, sender_account_id, contact_list_id, name, subject, status, created_at) "
                "VALUES (:u, :s, :l, 'camp', 'subj', 'DRAFT', :now)"
            ),
            {"u": user, "s": sender, "l": lst, "now": NOW},
        )
        conn.commit()
    tables = ["users", "contact_lists", "contacts", "contact_list_contacts", "sender_accounts", "campaigns"]

    def counts():
        with engine.connect() as conn:
            return {t: conn.execute(sa.text(f"SELECT COUNT(*) FROM {t}")).scalar() for t in tables}

    before = counts()
    assert all(n == 1 for n in before.values())

    command.upgrade(cfg, RECONCILE)

    assert counts() == before
    with engine.connect() as conn:
        assert conn.execute(sa.text("PRAGMA foreign_key_check")).all() == []
        assert conn.execute(sa.text("PRAGMA integrity_check")).scalar() == "ok"
    engine.dispose()


def test_guard_does_not_alter_runtime_engine(tmp_path):
    """Runtime connections keep SQLite's default (foreign_keys=OFF); the guard lives only in env.py."""
    import app.infrastructure.database as database

    with database.engine.connect() as conn:
        assert conn.execute(sa.text("PRAGMA foreign_keys")).scalar() == 0
    assert "foreign_keys" not in Path(database.__file__).read_text()
