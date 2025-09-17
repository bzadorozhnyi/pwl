import pytest


@pytest.mark.anyio
async def test_user_factories(ingredients_list_create_payload_factory):
    ingredients_list_create_payload_factory()
    ingredients_list_create_payload_factory(ingredients=5)
