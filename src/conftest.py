import asyncio
import os
import pkgutil
from unittest.mock import AsyncMock

import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.consts import ALEMBIC_CFG_PATH
from core.db import AsyncSessionProxy, get_session
from helpers.db import create_db, drop_db, is_db_exist
from main import app
from repositories.family import get_family_repository
from repositories.shopping_list import get_shopping_list_repository
from repositories.shopping_list_item import get_shopping_list_item_repository
from services.email import InMemoryEmailService, get_email_service
from services.recipe import RecipeService, get_recipe_service


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
def override_recipe_service(db_session):
    recipe_service = RecipeService(
        family_repository=get_family_repository(db_session),
        shopping_list_repository=get_shopping_list_repository(db_session),
        shopping_list_item_repository=get_shopping_list_item_repository(db_session),
    )

    async def fake_run(request: str):
        if "pasta" in request.lower():
            return AsyncMock(
                output={
                    "title": "Pasta",
                    "ingredients": [{"name": "Tomato", "quantity": "200 g"}],
                    "note": None,
                }
            )
        elif "salad" in request.lower():
            return AsyncMock(
                output={
                    "title": "Salad",
                    "ingredients": [{"name": "Cucumber", "quantity": "100 g"}],
                    "note": None,
                }
            )
        else:
            return AsyncMock(output={"error_message": "Invalid request"})

    mock_agent = AsyncMock()
    mock_agent.run.side_effect = fake_run
    recipe_service.recipe_gen_agent = mock_agent

    async def fake_merge_run(request: str, deps=None, **kwargs):
        if "cake" in request.lower():
            return AsyncMock(
                output={
                    "updated_items": [
                        {
                            "id": "4f311d46-dadf-4d07-80f6-013a4afebfcd",
                            "name": "Eggs – 10 pcs.",
                        }
                    ],
                    "new_items": [
                        {"name": "Cocoa powder – 100 g"},
                    ],
                }
            )
        else:
            return AsyncMock(output={"error_message": "Invalid request"})

    mock_merge_agent = AsyncMock()
    mock_merge_agent.run.side_effect = fake_merge_run
    recipe_service.recipe_merge_agent = mock_merge_agent

    return recipe_service


@pytest.fixture(scope="function")
def override_recipe_merge_service(db_session):
    recipe_service = RecipeService(
        family_repository=get_family_repository(db_session),
        shopping_list_repository=get_shopping_list_repository(db_session),
        shopping_list_item_repository=get_shopping_list_item_repository(db_session),
    )

    async def fake_run(request: str):
        if "cake" in request.lower():
            return AsyncMock(
                output={
                    "updated_items": [
                        {
                            "id": "4f311d46-dadf-4d07-80f6-013a4afebfcd",
                            "name": "Eggs – 10 pcs.",
                        }
                    ],
                    "new_items": [
                        {"name": "Cocoa powder – 100 g"},
                        {"name": "Sugar – 400 g"},
                        {"name": "Butter – 300 g"},
                        {"name": "Vanilla sugar – 20 g"},
                        {"name": "Milk – 500 ml"},
                        {"name": "Corn starch – 80 g"},
                        {"name": "Sour cream – 400 g"},
                        {"name": "Baking powder – 20 g"},
                        {"name": "Flour – 800 g"},
                    ],
                }
            )
        else:
            return AsyncMock(output={"error_message": "Invalid request"})

    mock_agent = AsyncMock()
    mock_agent.run.side_effect = fake_run
    recipe_service.recipe_merge_agent = mock_agent

    return recipe_service


@pytest.fixture(scope="function")
async def async_client(db_session, email_service, override_recipe_service):
    async def override_get_session():
        yield AsyncSessionProxy(db_session)

    app.dependency_overrides[get_session] = override_get_session

    app.dependency_overrides[get_email_service] = lambda: email_service

    app.dependency_overrides[get_recipe_service] = lambda: override_recipe_service

    async with AsyncClient(
        transport=ASGIWebSocketTransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


# Automatically load all fixture-factories from the tests/factories folder
pytest_plugins = [
    f"tests.factories.{modname}"
    for _, modname, _ in pkgutil.iter_modules(["tests/factories"])
]
