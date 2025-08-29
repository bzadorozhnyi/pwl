import uuid
from datetime import timedelta

import pytest
from fastapi import status
from sqlmodel import select

from core.jwt import AuthJWTService
from models.user import User
from models.verify_token import VerifyToken


@pytest.mark.anyio
async def test_request_forgot_password_with_unregistered_email(async_client):
    """Test that requesting password reset with unregistered email is handled gracefully."""
    payload = {"email": "unregistered@example.com"}
    response = await async_client.post("/api/auth/forgot-password/", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_request_forgot_password_success(
    async_client, user_factory, db_session, email_service):
    """Verify that requesting a forgot password for a registered user creates a VerifyToken
    and sends an email."""

    user = user_factory()

    payload = {"email": user.email}
    response = await async_client.post("/api/auth/forgot-password/", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    token = await db_session.scalar(
        select(VerifyToken).where(VerifyToken.email == user.email)
    )
    assert token is not None

    assert len(email_service.outbox) > 0
    sent_email = email_service.outbox[-1]
    assert sent_email["subject"] == "PWL Restore Password"
    assert sent_email["recipients"] == [user.email]


@pytest.mark.anyio
async def test_request_forgot_password_twice(async_client, user_factory, db_session):
    """Test that requesting a password reset twice for the same email is handled gracefully and don't create another verify token."""
    user = user_factory()

    payload = {"email": user.email}
    response = await async_client.post("/api/auth/forgot-password/", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    token = await db_session.scalar(
        select(VerifyToken).where(VerifyToken.email == user.email)
    )
    assert token is not None

    token_id = token.id

    response = await async_client.post("/api/auth/forgot-password/", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    token = await db_session.scalar(
        select(VerifyToken).where(VerifyToken.email == user.email)
    )
    assert token is not None

    assert token.id == token_id


@pytest.mark.anyio
async def test_update_forgot_password_with_invalid_token(async_client):
    """Test that updating password with an invalid token is rejected."""
    payload = {"token": str(uuid.uuid4()), "new_password": "new_password"}
    response = await async_client.post("/api/auth/reset-password/", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_forgot_password_with_expired_token(
    async_client, verify_token_factory
):
    """Test that updating password with an expired token is rejected."""
    verify_token = verify_token_factory()
    verify_token.created_at -= timedelta(days=1)

    payload = {"token": str(verify_token.token), "new_password": "new_password"}
    response = await async_client.post("/api/auth/reset-password/", json=payload)

    assert response.status_code == status.HTTP_410_GONE


@pytest.mark.anyio
async def test_update_forgot_password_success(async_client, user_factory, db_session):
    """Ensure that with a valid token, the password is updated and the VerifyToken is deleted."""
    user = user_factory()

    response = await async_client.post(
        "/api/auth/forgot-password/", json={"email": user.email}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    verify_token = await db_session.scalar(
        select(VerifyToken).where(VerifyToken.email == user.email)
    )
    assert verify_token is not None

    payload = {"token": str(verify_token.token), "new_password": "new_password"}
    update_response = await async_client.post("/api/auth/reset-password/", json=payload)

    assert update_response.status_code == status.HTTP_204_NO_CONTENT

    verify_token = await db_session.scalar(
        select(VerifyToken).where(VerifyToken.email == user.email)
    )
    assert verify_token is None

    user = await db_session.scalar(select(User).where(User.email == user.email))
    assert AuthJWTService().verify_password(payload["new_password"], user.password)
