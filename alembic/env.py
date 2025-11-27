"""Alembic env.py template adapted to read DATABASE_URL from environment
and to use robbot.infra.db.base.Base.metadata as target for autogenerate."""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from robbot.infra.db.base import Base
from robbot.infra.db import models  # noqa: F401 - import to register models

# this is the Alembic Config object, which provides access to the values within the .ini file
config = context.config  # type: ignore

# Interpret the config file for Python logging; this line sets up loggers.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url in alembic.ini with DATABASE_URL environment variable when present.
db_url = os.environ.get("DATABASE_URL")
if db_url:
    # alembic.ini may contain a placeholder; replace it so Alembic uses the container env var.
    config.set_main_option("sqlalchemy.url", db_url)

# Import your SQLAlchemy Base metadata here
# Ensure robbot.infra.db.base.Base is importable from the image (same PYTHONPATH)

target_metadata = getattr(Base, "metadata", None)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (apply to DB)."""
    configuration = config.get_section(config.config_ini_section, {})
    # Force UTF-8 encoding to prevent UnicodeDecodeError on Windows
    configuration["sqlalchemy.connect_args"] = {"client_encoding": "utf8"}

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
