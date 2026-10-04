from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy import pool

from alembic import context

from app.infrastructure.database import Base
import app.features.model_registry  # noqa: F401 - register all ORM metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def _disable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    # SQLite batch migrations rebuild tables with DROP/CREATE. With enforcement on, the DROP
    # of a parent table fires ON DELETE CASCADE and silently deletes child rows. The pragma
    # is a no-op inside a transaction, so it must run on the raw connection at connect time,
    # before SQLAlchemy/Alembic begin one. This engine is private to Alembic; application
    # connections (app.infrastructure.database) are not touched. If it cannot be disabled we abort
    # (fail closed) rather than risk silent data loss. See revision e5f6a7b8c9d0.
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("PRAGMA foreign_keys")
        if cursor.fetchone()[0] != 0:
            raise RuntimeError("Refusing to run migrations: could not disable SQLite foreign_keys")
    finally:
        cursor.close()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    if connectable.dialect.name == "sqlite":
        event.listen(connectable, "connect", _disable_sqlite_foreign_keys)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
