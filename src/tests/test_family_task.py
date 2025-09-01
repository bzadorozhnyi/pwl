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
        "assignee_id": {"type": "string", "format": "uuid"},
        "creator_id": {"type": "string", "format": "uuid"},
        "title": {"type": "string"},
        "done": {"type": "boolean"},
    },
    "required": ["id", "family_id", "assignee_id", "creator_id", "title", "done"],
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
        "/api/family-tasks/",
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
        "/api/family-tasks/",
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
        "/api/family-tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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
        "/api/family-tasks/",
        headers={"authorization": f"Bearer {access_token}"},
        json=payload,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def _assert_family_task_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=family_task_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")
