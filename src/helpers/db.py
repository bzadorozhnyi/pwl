from urllib.parse import urlparse, urlunparse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def get_db_name(db_url: str) -> str:
    return urlparse(db_url).path.lstrip("/")


def get_db_root_url(db_url: str) -> str:
    parsed = urlparse(db_url)
    return urlunparse(parsed._replace(path=""))


async def is_db_exist(db_url: str) -> bool:
    """
    Checks if a database exists.
    """
    engine = create_async_engine(db_url, echo=False, future=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        await engine.dispose()


async def drop_db(db_url: str) -> None:
    """
    Deletes a database using a connection to root_url.
    db_url is the url of the database to be deleted.
    """
    root_url = get_db_root_url(db_url)
    db_name = get_db_name(db_url)

    engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT", future=True)
    try:
        async with engine.connect() as conn:
            # terminate all connections to the database
            await conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :name
                    """
                ),
                {"name": db_name},
            )
            await conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
    finally:
        await engine.dispose()


async def create_db(db_url: str) -> None:
    """
    Creates a database using a connection to root_url.
    db_url is the url of the new database.
    """
    root_url = get_db_root_url(db_url)
    db_name = get_db_name(db_url)

    engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT", future=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        await engine.dispose()
