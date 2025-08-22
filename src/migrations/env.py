import asyncio
import importlib
import inspect
import os
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

import models
from core.config import settings


# This function dynamically imports all SQLModel table classes from the specified package.
# It ensures that every SQLModel with `table=True` in the package is registered in the global
# namespace, so that Alembic's `target_metadata` can automatically detect all tables
# for migration generation without manually importing each model.
def import_models_from_package(package):
    for loader, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, SQLModel)
                and getattr(obj, "__table__", None) is not None
            ):
                globals()[name] = obj


# Call the function on the models package to automatically import all SQLModel tables.
import_models_from_package(models)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# set used db url
db_url = os.getenv("DB_URL", settings.db_url)
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url() -> str:
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline():
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    url = get_url()
    connectable: AsyncEngine = create_async_engine(url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
