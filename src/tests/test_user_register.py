import pytest

@pytest.mark.anyio
async def test_user_register_success(async_client):
    response = await async_client.post(
        "/register/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_cannot_register_user_with_missing_fields(async_client):
    response = await async_client.post(
        "/register/",
        json={
            "email": "invalid_email",
        },
    )

    assert response.status_code == 422