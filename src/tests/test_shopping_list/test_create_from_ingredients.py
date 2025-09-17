import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.shopping_list import ShoppingList
from models.shopping_list_item import ShoppingListItem
from tests.test_shopping_list.schemas_utils import (
    _assert_shopping_list_response_schema,
    _assert_websocket_shopping_list_create_response_schema,
)
from tests.utils import get_access_token


@pytest.mark.anyio
async def test_create_from_ingredients_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    ingredients_list_create_payload_factory,
):
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    access_token = await get_access_token(async_client, user)

    payload = ingredients_list_create_payload_factory(family_id=str(family.id))

    response = await async_client.post(
        "/api/shopping-lists/from-ingredients/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED

    shopping_list = await db_session.scalar(
        select(ShoppingList).where(ShoppingList.creator_id == user.id)
    )
    assert shopping_list is not None
    assert shopping_list.creator_id == user.id
    assert shopping_list.family_id == family.id
    assert shopping_list.name == payload["title"]

    data = response.json()
    assert data["id"] == str(shopping_list.id)
    assert data["creator"]["id"] == str(user.id)
    assert data["family_id"] == str(family.id)
    assert data["name"] == payload["title"]

    items = (
        await db_session.scalars(
            select(ShoppingListItem).where(
                ShoppingListItem.shopping_list_id == shopping_list.id
            )
        )
    ).all()

    assert len(items) == len(payload["ingredients"])
    item_names = {item.name for item in items}
    payload_names = {ing["name"] for ing in payload["ingredients"]}

    assert item_names == payload_names

    _assert_shopping_list_response_schema(data)


@pytest.mark.anyio
async def test_cannot_create_from_ingredients_by_non_member(
    async_client, user_factory, family_factory, ingredients_list_create_payload_factory
):
    """Test that non-family member cannot create a shopping list from ingredients."""
    user = user_factory()
    family = family_factory()

    access_token = await get_access_token(async_client, user)

    payload = ingredients_list_create_payload_factory(family_id=str(family.id))
    response = await async_client.post(
        "/api/shopping-lists/from-ingredients/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
@pytest.mark.parametrize(
    "missing_field",
    ["title", "ingredients", "family_id"],
)
async def test_cannot_create_from_ingredients_with_missing_required_fields(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    ingredients_list_create_payload_factory,
    missing_field,
):
    """Test that cannot create a shopping list from ingredients with missing required fields."""

    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    access_token = await get_access_token(async_client, user)

    payload = ingredients_list_create_payload_factory(family_id=str(family.id))
    payload.pop(missing_field, None)

    response = await async_client.post(
        "/api/shopping-lists/from-ingredients/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_websocket_shopping_list_create_from_ingredients_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    ingredients_list_create_payload_factory,
):
    """Test WebSocket receives real-time creation events on shopping lists from ingredients."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    access_token = await get_access_token(async_client, user)

    async with aconnect_ws(
        "/api/ws/",
        async_client,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ws:
        payload = ingredients_list_create_payload_factory(family_id=str(family.id))
        await async_client.post(
            "/api/shopping-lists/from-ingredients/",
            headers={"authorization": f"Bearer {access_token}"},
            json=payload,
        )

        shopping_list = await db_session.scalar(
            select(ShoppingList).where(ShoppingList.creator_id == user.id)
        )
        response = await ws.receive_json()

        assert shopping_list is not None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_created_shopping_list"
        assert response["data"]["id"] == str(shopping_list.id)
        assert response["data"]["name"] == payload["title"]

        _assert_websocket_shopping_list_create_response_schema(response)
