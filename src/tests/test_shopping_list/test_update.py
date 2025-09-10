import uuid

import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlalchemy import select

from models.shopping_list import ShoppingList
from tests.test_shopping_list.schemas_utils import _assert_shopping_list_response_schema


@pytest.mark.anyio
async def test_update_shopping_list_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_update_payload_factory,
):
    """Test updating a shopping list."""
    user = user_factory()
    family = family_factory()
    family_member_factory(user_id=user.id, family_id=family.id)
    shopping_list = shopping_list_factory(creator_id=user.id, family_id=family.id)

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = shopping_list_update_payload_factory(name="Updated List")
    response = await async_client.put(
        f"/api/shopping-lists/{shopping_list.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    updated_shopping_list = await db_session.scalar(
        select(ShoppingList).where(ShoppingList.id == shopping_list.id)
    )

    assert updated_shopping_list.name == update_data["name"]
    _assert_shopping_list_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_update_nonexisting_shopping_list(
    async_client, user_factory, shopping_list_update_payload_factory
):
    """Test that user cannot update a non-existing shopping list."""
    user = user_factory()
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = shopping_list_update_payload_factory()
    response = await async_client.put(
        f"/api/shopping-lists/{str(uuid.uuid4())}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_cannot_update_with_empty_name(
    async_client, user_factory, shopping_list_update_payload_factory
):
    """Test that user cannot update a shopping list with an empty name."""
    user = user_factory()
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = shopping_list_update_payload_factory(name="")
    response = await async_client.put(
        f"/api/shopping-lists/{str(uuid.uuid4())}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_non_family_member_cannot_update_shopping_list(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_update_payload_factory,
):
    """Test that a user who is not a family member cannot update the shopping list."""
    user1 = user_factory()
    user2 = user_factory()

    family = family_factory()
    family_member_factory(user_id=user1.id, family_id=family.id)

    shopping_list = shopping_list_factory(creator_id=user1.id, family_id=family.id)

    payload = {"identifier": user2.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = shopping_list_update_payload_factory()
    response = await async_client.put(
        f"/api/shopping-lists/{shopping_list.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_update_shopping_list_creator(
    db_session,
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_update_payload_factory,
):
    """Test that user cannot update a shopping list's creator."""
    creator = user_factory()
    not_creator = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)
    family_member_factory(family_id=family.id, user_id=not_creator.id)

    shopping_list = shopping_list_factory(family_id=family.id, creator_id=creator.id)

    payload = {"identifier": creator.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = shopping_list_update_payload_factory()
    update_data["creator_id"] = str(not_creator.id)

    response = await async_client.put(
        f"/api/shopping-lists/{shopping_list.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    updated_shopping_list = await db_session.scalar(
        select(ShoppingList).where(ShoppingList.id == shopping_list.id)
    )

    assert updated_shopping_list.creator_id == creator.id  # should remain unchanged


@pytest.mark.anyio
async def test_cannot_update_shopping_list_family_id(
    db_session,
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_update_payload_factory,
):
    """Test that user cannot update a shopping list's family id."""
    user = user_factory()

    family1 = family_factory()
    family2 = family_factory()

    family_member_factory(family_id=family1.id, user_id=user.id)

    shopping_list = shopping_list_factory(family_id=family1.id, creator_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = shopping_list_update_payload_factory()
    update_data["family_id"] = str(family2.id)

    response = await async_client.put(
        f"/api/shopping-lists/{shopping_list.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    updated_shopping_list = await db_session.scalar(
        select(ShoppingList).where(ShoppingList.id == shopping_list.id)
    )

    assert updated_shopping_list.family_id == family1.id  # should remain unchanged


@pytest.mark.anyio
async def test_websocket_shopping_list_update_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_update_payload_factory,
):
    """Test WebSocket receives real-time update events on shopping lists."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    async with aconnect_ws(
        "/api/ws/",
        async_client,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ws:
        update_payload = shopping_list_update_payload_factory(family_id=str(family.id))
        await async_client.put(
            f"/api/shopping-lists/{shopping_list.id}/",
            headers={"authorization": f"Bearer {access_token}"},
            json=update_payload,
        )

        updated_shopping_list = await db_session.scalar(
            select(ShoppingList).where(ShoppingList.id == shopping_list.id)
        )
        response = await ws.receive_json()

        assert updated_shopping_list is not None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_updated_shopping_list"
        assert response["data"]["id"] == str(updated_shopping_list.id)
        assert response["data"]["name"] == update_payload["name"]

        _assert_shopping_list_response_schema(response["data"])
