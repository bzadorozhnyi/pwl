import pytest


@pytest.mark.anyio
async def test_shopping_list_item_factories(
    shopping_list_item_factory,
    shopping_list_item_create_payload_factory,
):
    shopping_list_item_factory()
    shopping_list_item_create_payload_factory()
