from collections import Counter

import pytest
from fastapi import status

from tests.test_family_task.schemas_utils import (
    _assert_family_task_list_response_schema,
)
from tests.utils import get_access_token


@pytest.mark.anyio
async def test_list_family_tasks_authentication_required(async_client, family_factory):
    """Test that authentication is required to list family tasks."""
    family = family_factory()

    response = await async_client.get(f"/api/tasks/{family.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_list_family_tasks_success(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that users can list their family tasks."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    family_tasks = family_task_factory.create_batch(
        3, family_id=family.id, creator_id=user.id
    )

    access_token = await get_access_token(async_client, user)

    response = await async_client.get(
        f"/api/tasks/{family.id}/",
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["count"] == 3
    assert data["next_page"] is None
    assert data["previous_page"] is None
    assert len(data["results"]) == 3

    returned_ids = [item["id"] for item in data["results"]]
    expected_ids = [str(task.id) for task in family_tasks]

    assert Counter(returned_ids) == Counter(expected_ids)

    _assert_family_task_list_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_list_other_family_tasks(
    async_client, user_factory, family_factory, family_member_factory
):
    """Test that user cannot list tasks from other families."""
    user1 = user_factory()
    user2 = user_factory()

    family1 = family_factory()
    family2 = family_factory()

    family_member_factory(family_id=family1.id, user_id=user1.id)
    family_member_factory(family_id=family2.id, user_id=user2.id)

    access_token = await get_access_token(async_client, user1)

    response = await async_client.get(
        f"/api/tasks/{family2.id}/",
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_paginated_list_family_tasks_multiple_pages(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that family tasks are listed with correct pagination over multiple pages."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    family_task_factory.create_batch(
        15, family_id=family.id, creator_id=user.id, assignee_id=user.id
    )

    access_token = await get_access_token(async_client, user)

    headers = {"authorization": f"Bearer {access_token}"}

    response = await async_client.get(
        f"/api/tasks/{family.id}/?page=1&page_size=10",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["count"] == 15
    assert len(data["results"]) == 10
    assert data["next_page"] is not None
    assert data["previous_page"] is None
    _assert_family_task_list_response_schema(data)

    next_url = data["next_page"]
    response2 = await async_client.get(next_url, headers=headers)
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()

    assert len(data2["results"]) == 5
    assert data2["next_page"] is None
    assert data2["previous_page"] is not None
    _assert_family_task_list_response_schema(data2)
