import uuid
from collections import Counter

import jsonschema
import pytest
from fastapi import status
from sqlmodel import select

from models.family_task import FamilyTask

family_task_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "family_id": {"type": "string", "format": "uuid"},
        "assignee": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["id", "first_name", "last_name"],
            "additionalProperties": False,
        },
        "creator": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["id", "first_name", "last_name"],
            "additionalProperties": False,
        },
        "title": {"type": "string"},
        "done": {"type": "boolean"},
    },
    "required": ["id", "family_id", "assignee", "creator", "title", "done"],
    "additionalProperties": False,
}


family_task_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next_page": {"type": ["string", "null"], "format": "uri"},
        "previous_page": {"type": ["string", "null"], "format": "uri"},
        "results": {"type": "array", "items": family_task_response_schema},
    },
    "required": ["count", "next_page", "previous_page", "results"],
    "additionalProperties": False,
}


@pytest.mark.anyio
async def test_create_family_task_success_assign_yourself(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_create_payload_factory,
):
    """Test successful creation of a family task by assigning it to yourself."""
    user = user_factory()
    family = family_factory()
    family_member = family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = family_task_create_payload_factory(
        family_id=str(family.id), assignee_id=str(family_member.user_id)
    )
    response = await async_client.post(
        "/api/tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    family_task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.creator_id == user.id)
    )
    assert family_task is not None
    assert family_task.creator_id == user.id
    assert family_task.assignee_id == user.id
    assert family_task.title == payload["title"]
    assert family_task.done is False

    _assert_family_task_response_schema(response.json())


@pytest.mark.anyio
async def test_create_family_task_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_create_payload_factory,
):
    """Test successful creation of a family task."""
    user = user_factory()
    other_user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    family_member_factory(family_id=family.id, user_id=other_user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = family_task_create_payload_factory(
        family_id=str(family.id), assignee_id=str(other_user.id)
    )
    response = await async_client.post(
        "/api/tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    family_task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.creator_id == user.id)
    )
    assert family_task is not None
    assert family_task.creator_id == user.id
    assert family_task.assignee_id == other_user.id
    assert family_task.title == payload["title"]
    assert family_task.done is False

    _assert_family_task_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_create_family_task_by_non_member(
    async_client, user_factory, family_factory, family_task_create_payload_factory
):
    """Test that non-family member cannot create a family task."""
    user = user_factory()
    family = family_factory()

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = family_task_create_payload_factory(
        family_id=str(family.id), assignee_id=str(user.id)
    )
    response = await async_client.post(
        "/api/tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_create_family_task_for_non_member(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_create_payload_factory,
):
    """Test that cannot create a family task for a non-member."""
    user = user_factory()
    user_not_from_family = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = family_task_create_payload_factory(
        family_id=str(family.id), assignee_id=str(user_not_from_family.id)
    )
    response = await async_client.post(
        "/api/tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
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

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

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

    payload = {"identifier": user1.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

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

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

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


@pytest.mark.anyio
async def test_update_family_task_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
    family_task_update_payload_factory,
):
    """Test updating a family task."""
    user1 = user_factory()
    user2 = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user1.id)
    family_member_factory(family_id=family.id, user_id=user2.id)

    task = family_task_factory(
        family_id=family.id, creator_id=user1.id, assignee_id=user1.id
    )

    payload = {"identifier": user1.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = family_task_update_payload_factory(
        assignee_id=str(user2.id), done=True
    )
    response = await async_client.put(
        f"/api/tasks/{task.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    family_task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.creator_id == user1.id)
    )

    assert family_task.title == update_data["title"]
    assert str(family_task.assignee_id) == update_data["assignee_id"]
    assert family_task.done == update_data["done"]
    _assert_family_task_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_update_nonexisting_task(
    async_client, user_factory, family_task_update_payload_factory
):
    """Test that user cannot update a non-existing task."""
    user = user_factory()
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = family_task_update_payload_factory()
    response = await async_client.put(
        f"/api/tasks/{str(uuid.uuid4())}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_family_task_only_creator(
    async_client,
    user_factory,
    family_task_update_payload_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that only the creator can update the task."""
    creator = user_factory()
    alignee = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)
    family_member_factory(family_id=family.id, user_id=alignee.id)

    task = family_task_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=alignee.id
    )

    payload = {"identifier": alignee.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = family_task_update_payload_factory()
    response = await async_client.put(
        f"/api/tasks/{task.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_update_with_invalid_assignee(
    async_client,
    user_factory,
    family_task_update_payload_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that user cannot update a task with an invalid assignee."""
    user1 = user_factory()
    user2 = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user1.id)

    task = family_task_factory(
        family_id=family.id, creator_id=user1.id, assignee_id=user1.id
    )

    payload = {"identifier": user1.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = family_task_update_payload_factory(
        assignee_id=str(user2.id), done=True
    )
    response = await async_client.put(
        f"/api/tasks/{task.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_cannot_update_with_empty_title(
    async_client,
    user_factory,
    family_task_update_payload_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that user cannot update a task with an empty title."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    task = family_task_factory(
        family_id=family.id, creator_id=user.id, assignee_id=user.id
    )

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = family_task_update_payload_factory(title="")
    response = await async_client.put(
        f"/api/tasks/{task.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_cannot_update_task_creator(
    db_session,
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that user cannot update a task's creator."""
    creator = user_factory()
    not_creator = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)
    family_member_factory(family_id=family.id, user_id=not_creator.id)

    task = family_task_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=creator.id
    )

    payload = {"identifier": creator.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = {"creator_id": str(not_creator.id)}
    response = await async_client.put(
        f"/api/tasks/{task.id}/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    updated_task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.id == task.id)
    )

    assert updated_task.creator_id == creator.id  # stay the same as before


@pytest.mark.anyio
@pytest.mark.parametrize(
    "role, initial_done, update_done",
    [
        pytest.param("creator", False, False, id="creator-False->False"),
        pytest.param("creator", False, True, id="creator-False->True"),
        pytest.param("creator", True, False, id="creator-True->False"),
        pytest.param("creator", True, True, id="creator-True->True"),
        pytest.param("assignee", False, False, id="assignee-False->False"),
        pytest.param("assignee", False, True, id="assignee-False->True"),
        pytest.param("assignee", True, False, id="assignee-True->False"),
        pytest.param("assignee", True, True, id="assignee-True->True"),
    ],
)
async def test_update_task_done_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
    role,
    initial_done,
    update_done,
):
    """Test that creator or assignee can update task's done status."""
    creator = user_factory()
    assignee = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)
    family_member_factory(family_id=family.id, user_id=assignee.id)

    task = family_task_factory(
        family_id=family.id,
        creator_id=creator.id,
        assignee_id=assignee.id,
        done=initial_done,
    )

    user = creator if role == "creator" else assignee
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == status.HTTP_200_OK
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = {"done": update_done}
    response = await async_client.patch(
        f"/api/tasks/{task.id}/done/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    updated_task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.id == task.id)
    )

    assert updated_task.done == update_data["done"]


@pytest.mark.anyio
async def test_update_task_done_not_found(
    async_client,
    user_factory,
):
    """Test updating non-existing task returns 404."""
    user = user_factory()
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = {"done": True}
    response = await async_client.patch(
        f"/api/tasks/{str(uuid.uuid4())}/done/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_task_done_forbidden(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that a user who is neither creator nor assignee cannot update done."""
    creator = user_factory()
    assignee = user_factory()
    other_user = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)
    family_member_factory(family_id=family.id, user_id=assignee.id)
    family_member_factory(family_id=family.id, user_id=other_user.id)

    task = family_task_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=assignee.id, done=False
    )

    payload = {"identifier": other_user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = {"done": True}
    response = await async_client.patch(
        f"/api/tasks/{task.id}/done/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "role",
    [
        pytest.param("creator", id="creator cannot update"),
        pytest.param("assignee", id="assignee cannot update"),
    ],
)
@pytest.mark.anyio
async def test_update_task_done_forbidden_for_non_family_member(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
    role,
):
    """Test that a user who is creator nor assignee cannot update done if not a family member."""
    creator = user_factory()
    assignee = user_factory()

    family = family_factory()
    if role == "creator":
        family_member_factory(family_id=family.id, user_id=assignee.id)
    else:
        family_member_factory(family_id=family.id, user_id=creator.id)

    task = family_task_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=assignee.id, done=False
    )

    user = creator if role == "creator" else assignee
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    update_data = {"done": True}
    response = await async_client.patch(
        f"/api/tasks/{task.id}/done/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_delete_family_task_by_creator_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that creator can delete the family task."""
    creator = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)

    family_task = family_task_factory(family_id=family.id, creator_id=creator.id)

    payload = {"identifier": creator.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/tasks/{str(family_task.id)}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.id == family_task.id)
    )
    assert task is None


@pytest.mark.anyio
async def test_delete_family_task_by_admin_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that admin can delete the family task."""
    admin = user_factory()
    user = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=admin.id, role="admin")
    family_member_factory(family_id=family.id, user_id=user.id, role="member")

    family_task = family_task_factory(family_id=family.id, creator_id=user.id)

    payload = {"identifier": admin.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/tasks/{str(family_task.id)}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.id == family_task.id)
    )
    assert task is None


@pytest.mark.anyio
async def test_delete_family_task_not_found(async_client, db_session, user_factory):
    """Test that deleting a non-existent family task returns 404."""
    user = user_factory()
    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/tasks/{str(uuid.uuid4())}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_cannot_delete_family_task_by_non_family_member(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that non-family member cannot delete the family task."""
    creator = user_factory()
    non_family_member = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)

    family_task = family_task_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=non_family_member.id
    )

    payload = {"identifier": non_family_member.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/tasks/{str(family_task.id)}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.id == family_task.id)
    )
    assert task is not None


@pytest.mark.anyio
async def test_cannot_delete_family_task_by_assignee(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that assignee cannot delete the family task."""
    creator = user_factory()
    assignee = user_factory()

    family = family_factory()
    family_member_factory(family_id=family.id, user_id=creator.id)
    family_member_factory(family_id=family.id, user_id=assignee.id)

    family_task = family_task_factory(
        family_id=family.id, creator_id=creator.id, assignee_id=assignee.id
    )

    payload = {"identifier": assignee.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    access_token = auth_response.json()["tokens"]["access_token"]

    response = await async_client.delete(
        f"/api/tasks/{str(family_task.id)}/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    task = await db_session.scalar(
        select(FamilyTask).where(FamilyTask.id == family_task.id)
    )
    assert task is not None


def _assert_family_task_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=family_task_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_family_task_list_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=family_task_list_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")
