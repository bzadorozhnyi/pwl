import uuid

import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.shopping_list import ShoppingList
from tests.test_shopping_list.schemas_utils import (
    _assert_websocket_shopping_list_delete_event_response_schema,
)


@pytest.mark.anyio
async def test_delete_shopping_list_by_creator_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
):
    """Test that user can delete the shopping list."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/shopping-lists/{shopping_list.id}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    shopping_list = await db_session.scalar(
        select(ShoppingList).where(ShoppingList.id == shopping_list.id)
    )
    assert shopping_list is None


@pytest.mark.anyio
async def test_delete_shopping_list_not_found(async_client, user_factory):
    """Test that deleting a non-existent shopping list returns 404."""
    user = user_factory()
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/shopping-lists/{uuid.uuid4()}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_cannot_delete_shopping_list_by_non_family_member(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
):
    """Test that non-family member cannot delete the shopping list."""
    creator = user_factory()
    non_family_member = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)

    shopping_list = shopping_list_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=non_family_member.id
    )

    payload = {"identifier": non_family_member.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/shopping-lists/{shopping_list.id}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    shopping_list = await db_session.scalar(
        select(ShoppingList).where(ShoppingList.id == shopping_list.id)
    )
    assert shopping_list is not None


@pytest.mark.anyio
async def test_websocket_shopping_list_delete_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
):
    """Test WebSocket receives real-time delete events on shopping lists."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(
        family_id=family.id, creator_id=user.id, assignee_id=user.id
    )

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
            f"/api/shopping-lists/{shopping_list.id}/",
            headers={"authorization": f"Bearer {access_token}"},
        )

        sl = await db_session.scalar(
            select(ShoppingList).where(ShoppingList.creator_id == user.id)
        )
        response = await ws.receive_json()

        assert sl is None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_deleted_shopping_list"
        assert response["data"]["id"] == str(shopping_list.id)

        _assert_websocket_shopping_list_delete_event_response_schema(response)
