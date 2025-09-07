import uuid

import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.family_task import FamilyTask
from tests.test_family_task.schemas_utils import (
    _assert_websocket_task_delete_response_schema,
)


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
async def test_cannot_delete_family_task_by_non_family_admin(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test that non-family admin cannot delete the family task."""
    creator = user_factory()
    non_family_admin = user_factory()

    family1 = family_factory()
    family_member_factory(family_id=family1.id, user_id=creator.id)

    family2 = family_factory()
    family_member_factory(
        family_id=family2.id, user_id=non_family_admin.id, role="admin"
    )

    family_task = family_task_factory(
        family_id=family1.id, creator_id=creator.id, assignee_id=non_family_admin.id
    )

    payload = {"identifier": non_family_admin.email, "password": "password"}
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


@pytest.mark.anyio
async def test_websocket_family_task_create_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_factory,
):
    """Test WebSocket receives real-time delete events on family tasks."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    family_task = family_task_factory(
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
            f"/api/tasks/{family_task.id}/",
            headers={"authorization": f"Bearer {access_token}"},
        )

        task = await db_session.scalar(
            select(FamilyTask).where(FamilyTask.creator_id == user.id)
        )
        response = await ws.receive_json()

        assert task is None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_deleted_task"
        assert response["data"]["id"] == str(family_task.id)

        _assert_websocket_task_delete_response_schema(response)
