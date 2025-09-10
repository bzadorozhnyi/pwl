"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.
"""

import asyncio

import pytest
from alembic import command
from alembic.script import ScriptDirectory

from core.config import settings
from helpers.db import create_db, drop_db, is_db_exist


@pytest.fixture(scope="session")
def revisions(alembic_config):
    """
    Collect all revisions from Alembic migration scripts.
    """
    revisions_dir = ScriptDirectory.from_config(alembic_config)
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()  # from oldest to newest
    return revisions


@pytest.mark.anyio
@pytest.mark.migration
async def test_migrations_stairway(alembic_config, revisions):
    """
    Ensure each migration can be upgraded, downgraded, and upgraded again.
    Helps catch forgotten downgrade() logic or typos in migrations.
    """
    if await is_db_exist(settings.test_db_url):
        await drop_db(settings.test_db_url)
    await create_db(settings.test_db_url)

    for revision in revisions:
        try:
            # Apply revision
            await asyncio.to_thread(command.upgrade, alembic_config, revision.revision)

            # Downgrade (for the very first migration use -1)
            await asyncio.to_thread(
                command.downgrade, alembic_config, revision.down_revision or "-1"
            )

            # Upgrade again to ensure consistency
            await asyncio.to_thread(command.upgrade, alembic_config, revision.revision)
        except Exception as e:
            raise RuntimeError(
                f"Migration failed on revision {revision.revision}"
            ) from e

    await drop_db(settings.test_db_url)
