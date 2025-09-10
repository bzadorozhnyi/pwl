import uuid

import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.shopping_list_item import ShoppingListItem
from tests.utils import get_access_token
from tests.test_shopping_list_item.schemas_utils import (
    _assert_websocket_shopping_list_item_delete_event_response_schema,
)


@pytest.mark.anyio
async def test_delete_shopping_list_item_by_family_member_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test that any family member can delete a shopping list item."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    shopping_list = shopping_list_factory(family_id=family.id)

    shopping_list_item = shopping_list_item_factory(shopping_list_id=shopping_list.id)

    access_token = await get_access_token(async_client, user)

    response = await async_client.delete(
        f"/api/shopping-list-items/{shopping_list_item.id}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    item = await db_session.scalar(
        select(ShoppingListItem).where(ShoppingListItem.id == shopping_list_item.id)
    )
    assert item is None


@pytest.mark.anyio
async def test_delete_shopping_list_item_not_found(async_client, user_factory):
    """Test that deleting a non-existent shopping list item returns 404."""
    user = user_factory()
    access_token = await get_access_token(async_client, user)

    response = await async_client.delete(
        f"/api/shopping-list-items/{uuid.uuid4()}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_shopping_list_item_by_non_family_member_forbidden(
    async_client,
    db_session,
    user_factory,
    family_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test that a non-family member cannot delete a shopping list item."""
    family = family_factory()
    shopping_list = shopping_list_factory(family_id=family.id)
    shopping_list_item = shopping_list_item_factory(shopping_list_id=shopping_list.id)

    non_family_member = user_factory()

    access_token = await get_access_token(async_client, non_family_member)

    response = await async_client.delete(
        f"/api/shopping-list-items/{shopping_list_item.id}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    item = await db_session.scalar(
        select(ShoppingListItem).where(ShoppingListItem.id == shopping_list_item.id)
    )
    assert item is not None


@pytest.mark.anyio
async def test_websocket_shopping_list_item_delete_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test WebSocket receives real-time delete events on shopping list items."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(
        family_id=family.id, creator_id=user.id, assignee_id=user.id
    )
    shopping_list_item = shopping_list_item_factory(shopping_list_id=shopping_list.id)

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    async with aconnect_ws(
        "/api/ws/",
        async_client,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ws:
        await async_client.delete(
            f"/api/shopping-list-items/{shopping_list_item.id}/",
            headers={"authorization": f"Bearer {access_token}"},
        )

        sli = await db_session.scalar(
            select(ShoppingListItem).where(ShoppingListItem.id == shopping_list_item.id)
        )
        response = await ws.receive_json()

        assert sli is None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_deleted_shopping_list_item"
        assert response["data"]["id"] == str(shopping_list_item.id)

        _assert_websocket_shopping_list_item_delete_event_response_schema(response)
