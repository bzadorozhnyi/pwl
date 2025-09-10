import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.shopping_list import ShoppingList
from tests.test_shopping_list.schemas_utils import (
    _assert_shopping_list_response_schema,
    _assert_websocket_shopping_list_create_response_schema,
)


@pytest.mark.anyio
async def test_create_shopping_list_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_create_payload_factory,
):
    """Test successful creation of a shopping list by a user."""

    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = shopping_list_create_payload_factory(family_id=str(family.id))
    response = await async_client.post(
        "/api/shopping-lists/",
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
    assert shopping_list.name == payload["name"]

    data = response.json()
    assert data["id"] == str(shopping_list.id)
    assert data["creator"]["id"] == str(user.id)
    assert data["family_id"] == str(family.id)
    assert data["name"] == payload["name"]

    _assert_shopping_list_response_schema(data)


@pytest.mark.anyio
async def test_cannot_create_shopping_list_by_non_member(
    async_client, user_factory, family_factory, shopping_list_create_payload_factory
):
    """Test that non-family member cannot create a shopping list."""
    user = user_factory()
    family = family_factory()

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = shopping_list_create_payload_factory(family_id=str(family.id))
    response = await async_client.post(
        "/api/shopping-lists/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_create_shopping_list_with_empty_name(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_create_payload_factory,
):
    """Test that cannot create a shopping list with an empty name."""

    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = shopping_list_create_payload_factory(family_id=str(family.id), name="")

    response = await async_client.post(
        "/api/shopping-lists/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_websocket_shopping_list_create_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_create_payload_factory,
):
    """Test WebSocket receives real-time creation events on shopping lists."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    async with aconnect_ws(
        "/api/ws/",
        async_client,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ws:
        payload = shopping_list_create_payload_factory(family_id=str(family.id))
        await async_client.post(
            "/api/shopping-lists/",
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
        assert response["data"]["name"] == payload["name"]

        _assert_websocket_shopping_list_create_response_schema(response)
