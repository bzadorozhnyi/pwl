import uuid

import pytest
from fastapi import status
from sqlmodel import select

from models.shopping_list_item import ShoppingListItem
from tests.test_shopping_list_item.schemas_utils import (
    _assert_shopping_list_item_response_schema,
)
from tests.utils import get_access_token


@pytest.mark.anyio
async def test_create_shopping_list_item_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_create_payload_factory,
):
    """Test successful creation of a shopping list item."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id)

    payload = shopping_list_item_create_payload_factory(
        shopping_list_id=str(shopping_list.id), name="Milk"
    )

    access_token = await get_access_token(async_client, user)

    response = await async_client.post(
        "/api/shopping-list-items/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    shopping_list_item = await db_session.scalar(
        select(ShoppingListItem).where(ShoppingListItem.creator_id == user.id)
    )
    assert shopping_list_item is not None
    assert shopping_list_item.creator_id == user.id
    assert shopping_list_item.shopping_list_id == shopping_list.id
    assert shopping_list_item.name == payload["name"]
    assert shopping_list_item.purchased is False

    data = response.json()
    assert data["shopping_list_id"] == str(shopping_list.id)
    assert data["name"] == payload["name"]
    assert data["creator"]["id"] == str(user.id)
    assert data["purchased"] is False

    _assert_shopping_list_item_response_schema(data)


@pytest.mark.anyio
async def test_cannot_create_shopping_list_item_by_non_member(
    async_client,
    user_factory,
    family_factory,
    shopping_list_factory,
    shopping_list_item_create_payload_factory,
):
    """Test that non-family member cannot create a shopping list item."""
    user = user_factory()
    family = family_factory()
    shopping_list = shopping_list_factory(family_id=family.id)

    access_token = await get_access_token(async_client, user)

    payload = shopping_list_item_create_payload_factory(
        shopping_list_id=str(shopping_list.id), name="Bread"
    )
    response = await async_client.post(
        "/api/shopping-list-items/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_create_shopping_list_item_with_empty_name(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_create_payload_factory,
):
    """Test that cannot create a shopping list item with an empty name."""

    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id)

    access_token = await get_access_token(async_client, user)

    payload = shopping_list_item_create_payload_factory(
        shopping_list_id=str(shopping_list.id), name=""
    )

    response = await async_client.post(
        "/api/shopping-list-items/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_cannot_create_shopping_list_item_with_nonexistent_shopping_list(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_item_create_payload_factory,
):
    """Test that creating a shopping list item with a nonexistent shopping_list_id returns 404."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    access_token = await get_access_token(async_client, user)

    payload = shopping_list_item_create_payload_factory(
        shopping_list_id=str(uuid.uuid4()), name="Eggs"
    )

    response = await async_client.post(
        "/api/shopping-list-items/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
