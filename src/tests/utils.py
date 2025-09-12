import pytest
from fastapi import status

from models.user import User


async def get_access_token(async_client, user: User) -> str:
    payload = {"identifier": user.email, "password": "password"}
    response = await async_client.post("/api/auth/token/", json=payload)

    if response.status_code != status.HTTP_200_OK:
        pytest.fail(
            f"Failed to get token: status={response.status_code} from {user.email}"
        )

    access_token = response.json().get("tokens", {}).get("access_token")
    if access_token is None:
        pytest.fail(f"Access token not returned for user {user.email}")

    return access_token
