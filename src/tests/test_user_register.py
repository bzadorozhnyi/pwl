import pytest
from fastapi import status
from sqlmodel import select

from models.user import User, UserRole


@pytest.mark.anyio
async def test_user_register_success(
    async_client, db_session, user_create_payload_factory
):
    payload = user_create_payload_factory()
    response = await async_client.post(
        "/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = await db_session.execute(
        select(User).where(User.email == payload["email"])
    )
    user = result.scalar_one_or_none()

    assert user is not None
    assert user.email == payload["email"]
    assert user.full_name == payload["full_name"]
    assert user.role == UserRole.USER


@pytest.mark.anyio
async def test_cannot_register_user_with_missing_fields(
    async_client,
    user_create_payload_factory,
):
    payload = user_create_payload_factory()
    payload.pop("full_name")
    payload.pop("password")

    response = await async_client.post(
        "/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_cannot_create_user_with_existing_email(
    async_client,
    user_factory,
    user_create_payload_factory,
):
    existing_user = user_factory()
    payload = user_create_payload_factory(email=existing_user.email)

    response = await async_client.post(
        "/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
