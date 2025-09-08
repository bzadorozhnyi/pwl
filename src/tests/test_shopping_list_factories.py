import pytest


@pytest.mark.anyio
async def test_shopping_list_factories(
    shopping_list_create_payload_factory,
):
    shopping_list_create_payload_factory()
