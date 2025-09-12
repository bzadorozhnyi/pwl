import jsonschema
import pytest
from fastapi import status

from tests.utils import get_access_token

user_profile_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "email": {"type": "string", "format": "email"},
        "username": {"type": "string"},
        "first_name": {"type": "string", "maxLength": 100},
        "last_name": {"type": "string", "maxLength": 100},
        "families": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "role": {"type": "string", "enum": ["admin", "member"]},
                },
                "required": ["id", "role"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["id", "email", "username", "first_name", "last_name", "families"],
    "additionalProperties": False,
}


@pytest.mark.anyio
async def test_retrieve_user_profile_success(
    async_client, user_factory, family_factory, family_member_factory
):
    """Test user profile retrieval."""
    user = user_factory(password="password")
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    access_token = await get_access_token(async_client, user)

    response = await async_client.get(
        "/api/users/profile/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json().get("id") == str(user.id)
    assert response.json().get("email") == user.email
    assert response.json().get("username") == user.username
    assert response.json().get("first_name") == user.first_name
    assert response.json().get("last_name") == user.last_name

    _assert_user_profile_response_schema(response.json())


@pytest.mark.anyio
async def test_cannot_retrieve_user_profile_unauthorized(async_client):
    """Test that cannot retrieve user profile without authorization."""
    response = await async_client.get("/api/users/profile/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_retrieve_user_profile_with_invalid_token(async_client):
    """Test that cannot retrieve user profile with invalid token."""
    response = await async_client.get(
        "/api/users/profile/",
        headers={
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4YWRkMTQ5ZC1mMDBjLTQ0ODEtOWZkNi0xNjMyODdlMWE2M2UiLCJleHAiOjE3NTY5OTA2ODl9.XAouQGb_OAiStJA6wIpm8PjNrkleyMlGs73qiJaAQAY"
        },
    )  # random jwt token
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_cannot_retrieve_user_profile_with_no_family(async_client, user_factory):
    """Test that cannot retrieve user profile if user is not in a family."""
    user = user_factory(password="password")

    access_token = await get_access_token(async_client, user)

    response = await async_client.get(
        "/api/users/profile/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def _assert_user_profile_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=user_profile_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")
