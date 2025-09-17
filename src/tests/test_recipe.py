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
    """Test the recipe service with various inputs."""
    user = user_factory()
    access_token = await get_access_token(async_client, user)

    response = await async_client.post(
        "/api/recipes/",
        json={"recipe_request": user_input},
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    response = response.json()

    if expected_title:
        assert response["title"] == expected_title
        assert response["ingredients"][0]["name"] == expected_name
    else:
        assert "error_message" in response


@pytest.mark.anyio
async def test_merge_with_shopping_list_not_found(async_client, user_factory):
    """Test that merging a recipe with a non-existent shopping list returns a 404 error."""
    user = user_factory()
    access_token = await get_access_token(async_client, user)
    non_existent_shopping_list_id = "00000000-0000-0000-0000-000000000000"

    response = await async_client.post(
        "/api/recipes/merge-with-shopping-list/",
        json={
            "recipe_request": "Give me a pasta recipe",
            "shopping_list_id": non_existent_shopping_list_id,
        },
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Shopping list not found"


@pytest.mark.anyio
async def test_merge_with_shopping_list_forbidden(
    async_client, user_factory, shopping_list_factory
):
    """Test that a user who is not a member of the family cannot merge a recipe with the shopping list."""
    user = user_factory()
    shopping_list = shopping_list_factory()
    access_token = await get_access_token(async_client, user)

    response = await async_client.post(
        "/api/recipes/merge-with-shopping-list/",
        json={
            "recipe_request": "Give me a pasta recipe",
            "shopping_list_id": str(shopping_list.id),
        },
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "User is not member of family"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_input,update_items_id,new_items_name",
    [
        (
            "Give me a cake recipe",
            "4f311d46-dadf-4d07-80f6-013a4afebfcd",
            "Cocoa powder – 100 g",
        ),
        ("Tell me a joke", None, None),
    ],
)
async def test_recipe_merge_with_shopping_list_service_param(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    user_input,
    update_items_id,
    new_items_name,
):
    """Test the recipe merge with shopping list for various inputs."""
    user = user_factory()
    family = family_factory()
    family_member_factory(user_id=user.id, family_id=family.id)
    shopping_list = shopping_list_factory(family_id=family.id)

    access_token = await get_access_token(async_client, user)

    response = await async_client.post(
        "/api/recipes/merge-with-shopping-list/",
        json={"recipe_request": user_input, "shopping_list_id": str(shopping_list.id)},
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    response = response.json()

    if update_items_id:
        assert response["updated_items"][0]["id"] == update_items_id
        assert response["new_items"][0]["name"] == new_items_name
    else:
        assert "error_message" in response
