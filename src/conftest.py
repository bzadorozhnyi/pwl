import asyncio
import os
import pkgutil

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.consts import ALEMBIC_CFG_PATH
from core.db import AsyncSessionProxy, get_session
from helpers.db import create_db, drop_db, is_db_exist
from main import app
from services.email import InMemoryEmailService, get_email_service


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def alembic_config():
    os.environ["DB_URL"] = settings.test_db_url
    cfg = Config(ALEMBIC_CFG_PATH)
    return cfg


@pytest.fixture(scope="session")
async def async_engine(alembic_config):
    if await is_db_exist(settings.test_db_url):
        await drop_db(settings.test_db_url)
    await create_db(settings.test_db_url)

    await asyncio.to_thread(command.upgrade, alembic_config, "head")

    engine = create_async_engine(settings.test_db_url, echo=True, future=True)

    yield engine

    await engine.dispose()
    await drop_db(settings.test_db_url)


@pytest.fixture(scope="session")
def async_session(async_engine):
    return sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def db_session(async_engine, async_session):
    async with async_engine.connect() as conn:
        transaction = await conn.begin()
        async with async_session(bind=conn) as session:
            yield session
            await session.close()
        await transaction.rollback()


@pytest.fixture(scope="function")
def email_service() -> InMemoryEmailService:
    return InMemoryEmailService(sender="test@example.com")


@pytest.fixture(scope="function")
async def async_client(db_session, email_service):
    async def override_get_session():
        yield AsyncSessionProxy(db_session)

    app.dependency_overrides[get_session] = override_get_session

    app.dependency_overrides[get_email_service] = lambda: email_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000/",
    ) as client:
        yield client


# Automatically load all fixture-factories from the tests/factories folder
pytest_plugins = [
    f"tests.factories.{modname}"
    for _, modname, _ in pkgutil.iter_modules(["tests/factories"])
]
