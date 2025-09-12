import uuid

import pytest
from fastapi import status
from sqlmodel import select

from models.shopping_list_item import ShoppingListItem
from tests.utils import get_access_token


@pytest.mark.anyio
@pytest.mark.parametrize(
    "initial_purchased, update_purchased",
    [
        pytest.param(False, False, id="False->False"),
        pytest.param(False, True, id="False->True"),
        pytest.param(True, False, id="True->False"),
        pytest.param(True, True, id="True->True"),
    ],
)
async def test_update_shopping_list_item_purchase_success(
    async_client,
    db_session,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
    initial_purchased,
    update_purchased,
):
    """Test that any family member can update shopping list item's purchased status."""
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)

    shopping_list = shopping_list_factory(family_id=family.id)

    item = shopping_list_item_factory(
        family_id=family.id,
        shopping_list_id=shopping_list.id,
        purchased=initial_purchased,
    )

    access_token = await get_access_token(async_client, user)

    update_data = {"purchased": update_purchased}
    response = await async_client.patch(
        f"/api/shopping-list-items/{item.id}/purchased/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    updated_item = await db_session.scalar(
        select(ShoppingListItem).where(ShoppingListItem.id == item.id)
    )
    assert updated_item.purchased == update_data["purchased"]


@pytest.mark.anyio
async def test_update_shopping_list_item_purchase_not_found(
    async_client,
    user_factory,
):
    """Test updating non-existing shopping list item purchase returns 404."""
    user = user_factory()
    access_token = await get_access_token(async_client, user)

    update_data = {"purchased": True}
    response = await async_client.patch(
        f"/api/shopping-list-items/{uuid.uuid4()}/purchased/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_shopping_list_item_purchase_only_family_member_can_update(
    async_client,
    db_session,
    user_factory,
    family_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    """Test that only a family member can update shopping list item's purchased status."""
    family = family_factory()
    shopping_list = shopping_list_factory(family_id=family.id)
    item = shopping_list_item_factory(
        family_id=family.id,
        shopping_list_id=shopping_list.id,
        purchased=False,
    )

    non_family_member = user_factory()

    access_token = await get_access_token(async_client, non_family_member)

    update_data = {"purchased": True}
    response = await async_client.patch(
        f"/api/shopping-list-items/{item.id}/purchased/",
        json=update_data,
        headers={"authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    updated_item = await db_session.scalar(
        select(ShoppingListItem).where(ShoppingListItem.id == item.id)
    )
    assert updated_item.purchased is False  # remain the same
