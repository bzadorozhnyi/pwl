import pytest
from fastapi import status
from httpx_ws import aconnect_ws
from sqlmodel import select

from models.family_task import FamilyTask
from tests.test_family_task.schemas_utils import (
    _assert_family_task_response_schema,
    _assert_websocket_task_create_response_schema,
)


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
async def test_cannot_create_family_task_with_empty_title(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_create_payload_factory,
):
    """Test that cannot create a family task with an empty title."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

    payload = family_task_create_payload_factory(
        family_id=str(family.id), assignee_id=str(user.id), title=""
    )
    response = await async_client.post(
        "/api/tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_websocket_family_task_create_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    family_task_create_payload_factory,
):
    """Test WebSocket receives real-time creation events on family tasks."""
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
        payload = family_task_create_payload_factory(
            family_id=str(family.id), assignee_id=str(user.id)
        )
        await async_client.post(
            "/api/tasks/",
            headers={"authorization": f"Bearer {access_token}"},
            json=payload,
        )

        family_task = await db_session.scalar(
            select(FamilyTask).where(FamilyTask.creator_id == user.id)
        )
        response = await ws.receive_json()

        assert family_task is not None
        assert response["family_id"] == str(family.id)
        assert response["event_type"] == "user_created_task"
        assert response["data"]["id"] == str(family_task.id)
        assert response["data"]["title"] == payload["title"]

        _assert_websocket_task_create_response_schema(response)
