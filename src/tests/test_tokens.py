import jsonschema
import pytest
from fastapi import status

user_auth_response_schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "email": {"type": "string", "format": "email"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
            },
            "required": [
                "id",
                "email",
                "first_name",
                "last_name",
                "created_at",
                "updated_at",
            ],
            "additionalProperties": False,
        },
        "tokens": {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "refresh_token": {"type": "string"},
                "token_type": {"type": "string"},
            },
            "required": ["access_token", "refresh_token", "token_type"],
            "additionalProperties": False,
        },
    },
    "required": ["user", "tokens"],
    "additionalProperties": False,
}

access_token_response_schema = {
    "type": "object",
    "properties": {
        "access_token": {"type": "string"},
    },
    "required": ["access_token"],
    "additionalProperties": False,
}


@pytest.mark.anyio
async def test_user_login_success_by_email(async_client, user_factory):
    """Test that user can successfully login by email."""
    user = user_factory(password="password")

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["user"]["email"] == user.email

    _assert_user_auth_response_schema(response.json())


@pytest.mark.anyio
async def test_user_login_success_by_username(async_client, user_factory):
    """Test that user can successfully login by username."""
    user = user_factory(username="test_user", password="password")

    payload = {"identifier": user.username, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["user"]["email"] == user.email

    _assert_user_auth_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_login_with_nonexisting_email(async_client):
    """Test that user cannot login with non-existing email."""
    payload = {"identifier": "nonexisting@example.com", "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_cannot_login_with_invalid_password(async_client, user_factory):
    """Test that user cannot login with invalid password."""
    user = user_factory(password="password")

    payload = {"identifier": user.email, "password": "invalid_password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_user_cannot_login_with_missing_password(async_client, user_factory):
    """Test that user cannot login with missing password."""
    user = user_factory(password="password")

    payload = {"identifier": user.email}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_retrieve_access_token_with_refresh_token_success(
    async_client, user_factory
):
    """Test that user can successfully retrieve access token with refresh token."""
    user = user_factory(password="password")

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    refresh_token = response.json().get("tokens", {}).get("refresh_token")

    assert refresh_token is not None
    response = await async_client.post(
        "/api/auth/token/refresh/", json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK
    _assert_access_token_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_retrieve_access_token_without_refresh_token(async_client):
    """Test that user cannot retrieve access token without refresh token."""
    response = await async_client.post(
        "/api/auth/token/refresh/",
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_cannot_retrieve_access_token_with_invalid_refresh_token(async_client):
    """Test that user cannot retrieve access token with invalid refresh token."""
    response = await async_client.post(
        "/api/auth/token/refresh/",
        json={
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjMsImV4cCI6MTc1NTc3MDMxMn0.x1hHi8YOVAqQogszajavnIV2-nb__KTp5ccL8khG5pd"  # random jwt token
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def _assert_user_auth_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=user_auth_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")


def _assert_access_token_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=access_token_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")
