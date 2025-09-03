import jsonschema
import pytest
from fastapi import status
from sqlmodel import select

from models.family import FamilyMember, FamilyRole
from models.user import User

user_register_response_schema = {
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


@pytest.mark.anyio
async def test_user_register_success(
    async_client, db_session, user_create_payload_factory
):
    """Test that user can register successfully."""
    payload = user_create_payload_factory()
    response = await async_client.post(
        "/api/auth/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = await db_session.scalar(select(User).where(User.email == payload["email"]))

    assert user is not None
    assert user.email == payload["email"]
    assert user.first_name == payload["first_name"]
    assert user.last_name == payload["last_name"]

    family_member = await db_session.scalar(
        select(FamilyMember).where(FamilyMember.user_id == user.id)
    )
    assert family_member is not None
    assert family_member.user_id == user.id
    assert family_member.role == FamilyRole.ADMIN

    _assert_user_register_response_schema(response.json())


@pytest.mark.anyio
@pytest.mark.parametrize("field", ["email", "password", "first_name", "last_name"])
async def test_cannot_register_user_with_missing_fields(
    async_client,
    user_create_payload_factory,
    field,
):
    """Test that user cannot register with missing fields."""
    payload = user_create_payload_factory()
    payload.pop(field)

    response = await async_client.post(
        "/api/auth/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
@pytest.mark.parametrize("name", ["first_name", "last_name"])
async def test_cannot_register_user_with_empty_name(
    async_client,
    user_create_payload_factory,
    name,
):
    """Test that user cannot register with empty first or last name."""
    payload = user_create_payload_factory()
    payload[name] = ""

    response = await async_client.post(
        "/api/auth/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_cannot_create_user_with_existing_email(
    async_client,
    user_factory,
    user_create_payload_factory,
):
    """Test that user cannot create with existing email."""
    existing_user = user_factory()
    payload = user_create_payload_factory(email=existing_user.email)

    response = await async_client.post(
        "/api/auth/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_cannot_register_with_short_password(
    async_client, user_create_payload_factory
):
    """Test that user cannot register with short password (less than 8 symbols)."""
    payload = user_create_payload_factory(password="1234567")  # less than 8 symbols

    response = await async_client.post(
        "/api/auth/register/",
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def _assert_user_register_response_schema(data):
    """Validate that the response matches the expected schema."""
    try:
        jsonschema.validate(instance=data, schema=user_register_response_schema)
    except jsonschema.exceptions.ValidationError as e:
        pytest.fail(f"Response does not match schema: {e}")
