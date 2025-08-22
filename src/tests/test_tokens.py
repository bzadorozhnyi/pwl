import jsonschema
import pytest
from fastapi import status

user_auth_response_schema = {
    "type": "object",
    "properties": {
        "access_token": {"type": "string"},
        "refresh_token": {"type": "string"},
        "token_type": {"type": "string"},
    },
    "required": ["access_token", "refresh_token", "token_type"],
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
async def test_user_login_success(async_client, user_factory):
    """Test that user can successfully login."""
    user = user_factory(password="password")

    payload = {"email": user.email, "password": "password"}
    response = await async_client.post("/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    _assert_user_auth_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_login_with_invalid_email(async_client):
    """Test that user cannot login with invalid email."""
    payload = {"email": "invalid@example.com", "password": "password"}
    response = await async_client.post("/token/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_cannot_login_with_invalid_password(async_client, user_factory):
    """Test that user cannot login with invalid password."""
    user = user_factory(password="password")

    payload = {"email": user.email, "password": "invalid_password"}
    response = await async_client.post("/token/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_user_cannot_login_with_missing_password(async_client, user_factory):
    """Test that user cannot login with missing password."""
    user = user_factory(password="password")

    payload = {"email": user.email}
    response = await async_client.post("/token/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_retrieve_access_token_with_refresh_token_success(
    async_client, user_factory
):
    """Test that user can successfully retrieve access token with refresh token."""
    user = user_factory(password="password")

    payload = {"email": user.email, "password": "password"}
    response = await async_client.post("/token/", json=payload)

    refresh_token = response.json().get("refresh_token")

    assert refresh_token is not None
    response = await async_client.post(
        "/token/refresh/", json={"refresh_token": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK
    _assert_access_token_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_retrieve_access_token_without_refresh_token(async_client):
    """Test that user cannot retrieve access token without refresh token."""
    response = await async_client.post(
        "/token/refresh/",
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_cannot_retrieve_access_token_with_invalid_refresh_token(async_client):
    """Test that user cannot retrieve access token with invalid refresh token."""
    response = await async_client.post(
        "/token/refresh/",
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
