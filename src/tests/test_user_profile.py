import jsonschema
import pytest
from fastapi import status

user_profile_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "email": {"type": "string", "format": "email"},
        "username": {"type": "string"},
        "first_name": {"type": "string", "maxLength": 100},
        "last_name": {"type": "string", "maxLength": 100},
        "role": {"type": "string", "enum": ["admin", "member"]},
    },
    "required": ["id", "email", "username", "first_name", "last_name", "role"],
    "additionalProperties": False,
}


@pytest.mark.anyio
async def test_retrieve_user_profile_success(
    async_client, db_session, user_factory, family_factory
):
    user = user_factory(password="password")
    await db_session.flush()
    family_factory(user_id=user.id)

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

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
    response = await async_client.get("/api/users/profile/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cannot_retrieve_user_profile_with_no_family(async_client, user_factory):
    user = user_factory(password="password")

    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get("tokens", {}).get("access_token")
    assert access_token is not None

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
