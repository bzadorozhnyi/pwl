import uuid

import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.family_task import FamilyTask
from tests.test_family_task.schemas_utils import (
    _assert_family_task_response_schema,
    _assert_websocket_task_update_done_status_response_schema,
    _assert_websocket_task_update_response_schema,
)


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
async def test_websocket_family_task_update_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
    family_task_update_payload_factory,
):
    """Test WebSocket receives real-time update events on family tasks."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    family_task = family_task_factory(
        family_id=family.id, creator_id=user.id, assignee_id=user.id
    )

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["tokens"]["access_token"]

    async with aconnect_ws(
        "/api/ws/",
        async_client,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ws:
        payload = family_task_update_payload_factory(
            family_id=str(family.id), assignee_id=str(user.id)
        )
        await async_client.put(
            f"/api/tasks/{family_task.id}/",
            headers={"authorization": f"Bearer {access_token}"},
            json=payload,
        )

        family_task = await db_session.scalar(
            select(FamilyTask).where(FamilyTask.creator_id == user.id)
        )
        response = await ws.receive_json()

        assert family_task is not None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_updated_task"
        assert response["data"]["id"] == str(family_task.id)
        assert response["data"]["title"] == payload["title"]

        _assert_websocket_task_update_response_schema(response)


@pytest.mark.anyio
async def test_websocket_update_task_done_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test WebSocket receives real-time done state update events on family tasks."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    family_task = family_task_factory(
        family_id=family.id, creator_id=user.id, assignee_id=user.id, done=False
    )

    payload = {"identifier": user.email, "password": "password"}
    auth_response = await async_client.post("/api/auth/token/", json=payload)
    assert auth_response.status_code == 200
    access_token = auth_response.json()["tokens"]["access_token"]

    async with aconnect_ws(
        "/api/ws/",
        async_client,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ws:
        update_payload = {"done": True}
        response = await async_client.patch(
            f"/api/tasks/{family_task.id}/done/",
            json=update_payload,
            headers={"authorization": f"Bearer {access_token}"},
        )

        family_task = await db_session.scalar(
            select(FamilyTask).where(FamilyTask.creator_id == user.id)
        )
        response = await ws.receive_json()

        assert family_task is not None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_updated_task_done_status"
        assert response["data"]["id"] == str(family_task.id)
        assert response["data"]["done"] == update_payload["done"]

        _assert_websocket_task_update_done_status_response_schema(response)
