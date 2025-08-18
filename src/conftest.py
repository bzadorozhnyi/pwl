import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.config import settings
from core.consts import ALEMBIC_CFG_PATH
from core.db import get_session
from main import app

engine = create_async_engine(settings.test_db_url, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# @pytest.fixture(scope="module")
# def setup_db():
#     alembic_cfg = Config(ALEMBIC_CFG_PATH)

#     alembic_cfg.set_main_option("sqlalchemy.url", settings.test_db_url)

#     command.upgrade(alembic_cfg, "head")

#     yield engine

#     command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
async def db_session(setup_db):
    async with setup_db.connect() as conn:
        transaction = await conn.begin()
        async with async_session(bind=conn) as session:
            yield session
            await session.close()
        await transaction.rollback()


@pytest.fixture(scope="function")
async def async_client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000/",
    ) as client:
        yield client
