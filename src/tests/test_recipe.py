import pytest
from fastapi import status

from tests.utils import get_access_token


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_input,expected_title,expected_name",
    [
        ("Give me a pasta recipe", "Pasta", "Tomato"),
        ("Give me a salad recipe", "Salad", "Cucumber"),
        ("Tell me a joke", None, None),
    ],
)
async def test_recipe_service_param(
    user_factory, async_client, user_input, expected_title, expected_name
):
    user = user_factory()
    access_token = await get_access_token(async_client, user)

    response = await async_client.post(
        "/api/recipes/",
        json={"request": user_input},
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    response = response.json()

    if expected_title:
        assert response["title"] == expected_title
        assert response["ingredients"][0]["name"] == expected_name
    else:
        assert "error_message" in response
