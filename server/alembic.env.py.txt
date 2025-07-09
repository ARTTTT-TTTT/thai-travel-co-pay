import asyncio
import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.configs.app_config import app_config
from app.database.base import Base
from app.models import *  # type: ignore # noqa: F403

# Alembic Config
config = context.config

# Setup loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata
target_metadata = Base.metadata


config.set_main_option(
    "sqlalchemy.url",
    str(app_config.SQLALCHEMY_DATABASE_URI).replace("postgresql+asyncpg://", "postgresql://"),
)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode using async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )

        with context.begin_transaction():
            context.run_migrations()

    await connectable.dispose()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


main()
