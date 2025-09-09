import uuid
from collections import Counter

import pytest
from fastapi import status

from tests.test_shopping_list_item.schemas_utils import (
    _assert_shopping_list_item_list_response_schema,
)


@pytest.mark.anyio
async def test_retrieve_all_shopping_list_items_authentication_required(
    async_client, shopping_list_factory
):
    """Test that authentication is required to retrieve all shopping list items."""
    shopping_list = shopping_list_factory()

    response = await async_client.get(f"/api/shopping-lists/{shopping_list.id}/items")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_list_shopping_list_items_nonexistent_shopping_list_returns_404(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
):
    """Test that requesting items for a nonexistent shopping_list_id returns 404."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    response = await async_client.get(
        f"/api/shopping-lists/{uuid.uuid4()}/items",
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_list_shopping_list_items_success(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test that users can list their family's shopping list items."""

    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    shopping_list_items = shopping_list_item_factory.create_batch(
        3, shopping_list_id=shopping_list.id, creator_id=user.id
    )

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    response = await async_client.get(
        f"/api/shopping-lists/{shopping_list.id}/items",
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["count"] == 3
    assert data["next_page"] is None
    assert data["previous_page"] is None
    assert len(data["results"]) == 3

    returned_ids = [item["id"] for item in data["results"]]
    expected_ids = [str(s.id) for s in shopping_list_items]

    assert Counter(returned_ids) == Counter(expected_ids)

    _assert_shopping_list_item_list_response_schema(data)


@pytest.mark.anyio
async def test_cannot_list_items_from_other_family_shopping_list(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test that user cannot list items from a shopping list belonging to another family."""

    user1 = user_factory()
    user2 = user_factory()
    family1 = family_factory()
    family2 = family_factory()

    family_member_factory(family_id=family1.id, user_id=user1.id)
    family_member_factory(family_id=family2.id, user_id=user2.id)

    shopping_list_other_family = shopping_list_factory(
        family_id=family2.id, creator_id=user2.id
    )
    shopping_list_item_factory.create_batch(
        2, shopping_list_id=shopping_list_other_family.id, creator_id=user2.id
    )

    payload = {"identifier": user1.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    response = await async_client.get(
        f"/api/shopping-lists/{shopping_list_other_family.id}/items",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_paginated_list_shopping_list_items_multiple_pages(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test that shopping list items are listed with correct pagination over multiple pages."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    shopping_list_item_factory.create_batch(
        15, shopping_list_id=shopping_list.id, creator_id=user.id
    )

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    headers = {"authorization": f"Bearer {access_token}"}

    response = await async_client.get(
        f"/api/shopping-lists/{shopping_list.id}/items?page=1&page_size=10",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["count"] == 15
    assert len(data["results"]) == 10
    assert data["next_page"] is not None
    assert data["previous_page"] is None
    _assert_shopping_list_item_list_response_schema(data)

    next_url = data["next_page"]
    response2 = await async_client.get(next_url, headers=headers)
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()

    assert len(data2["results"]) == 5
    assert data2["next_page"] is None
    assert data2["previous_page"] is not None
    _assert_shopping_list_item_list_response_schema(data2)
