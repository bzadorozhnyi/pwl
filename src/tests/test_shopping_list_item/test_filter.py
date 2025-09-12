from datetime import datetime, timedelta
from urllib.parse import urlencode

import pytest
from fastapi import status

from tests.test_shopping_list_item.schemas_utils import (
    _assert_shopping_list_item_list_response_schema,
)
from tests.utils import get_access_token


@pytest.mark.anyio
@pytest.mark.parametrize(
    "filter_params,expected_names",
    [
        ({"name": "Apple Green"}, ["Green Apple"]),
        ({"name": "Milk"}, ["Milk", "Almond Milk"]),
        ({"name": "Bread"}, ["Bread"]),
        ({"name": "Eggs"}, ["Eggs"]),
        ({"name": "Milk Bread"}, []),
        ({"name": "Almond"}, ["Almond Milk"]),
        (
            {
                "created_from": (
                    datetime.now() - timedelta(days=1, hours=12)
                ).isoformat()
            },
            ["Bread", "Eggs", "Almond Milk", "Green Apple"],
        ),
        (
            {"created_to": (datetime.now() - timedelta(days=1, hours=12)).isoformat()},
            ["Milk"],
        ),
    ],
)
async def test_filter_items(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
    filter_params,
    expected_names,
):
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    now = datetime.now()
    items = [
        {"name": "Milk", "created_at": now - timedelta(days=2)},
        {"name": "Bread", "created_at": now - timedelta(days=1)},
        {"name": "Eggs", "created_at": now},
        {"name": "Almond Milk", "created_at": now},
        {"name": "Green Apple", "created_at": now},
    ]
    for item in items:
        shopping_list_item_factory(
            shopping_list_id=shopping_list.id,
            creator_id=user.id,
            name=item["name"],
            created_at=item["created_at"],
        )

    access_token = await get_access_token(async_client, user)

    params = filter_params.copy()
    response = await async_client.get(
        f"/api/shopping-lists/{shopping_list.id}/items/?{urlencode(params)}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    names = [item["name"] for item in data["results"]]

    assert sorted(names) == sorted(expected_names)

    _assert_shopping_list_item_list_response_schema(data)


@pytest.mark.anyio
async def test_filter_items_by_date_and_pagination(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    shopping_list_item_factory,
):
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    now = datetime.now()
    # Create 20 items, each created_at one hour apart
    items = []
    for i in range(20):
        created_at = now - timedelta(hours=20 - i)
        shopping_list_item_factory(
            shopping_list_id=shopping_list.id,
            creator_id=user.id,
            name=f"Item {i + 1}",
            created_at=created_at,
        )
        items.append({"name": f"Item {i + 1}", "created_at": created_at})

    # Filter to get items 3 to 17 (inclusive) by created_at
    created_from = items[2]["created_at"].isoformat()
    created_to = items[16]["created_at"].isoformat()

    access_token = await get_access_token(async_client, user)

    params = {
        "created_from": created_from,
        "created_to": created_to,
    }

    # Check the first page (should have 10 items)
    response = await async_client.get(
        f"/api/shopping-lists/{shopping_list.id}/items/?{urlencode(params)}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["count"] == 15
    assert len(data["results"]) == 10
    expected_names = [f"Item {i + 1}" for i in range(2, 12)]
    actual_names = [item["name"] for item in data["results"]]
    assert actual_names == expected_names

    _assert_shopping_list_item_list_response_schema(data)

    # Check the second page (should have 5 remaining items)
    next_url = data["next_page"]
    response2 = await async_client.get(
        next_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response2.status_code == status.HTTP_200_OK

    data2 = response2.json()
    assert len(data2["results"]) == 5
    expected_names2 = [f"Item {i + 1}" for i in range(12, 17)]
    actual_names2 = [item["name"] for item in data2["results"]]
    assert actual_names2 == expected_names2

    _assert_shopping_list_item_list_response_schema(data2)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "filter_params,expected_status,expected_detail",
    [
        (
            {"name": "word " * 11},  # 11 words
            status.HTTP_400_BAD_REQUEST,
            "Too many words in search filter",
        ),
        (
            {"name": "one two three four five six seven eight nine ten"},  # 10 words
            status.HTTP_200_OK,
            None,
        ),
    ],
)
async def test_filter_items_name_word_limit(
    async_client,
    user_factory,
    family_factory,
    family_member_factory,
    shopping_list_factory,
    filter_params,
    expected_status,
    expected_detail,
):
    user = user_factory()
    family = family_factory()
    family_member_factory(family_id=family.id, user_id=user.id)
    shopping_list = shopping_list_factory(family_id=family.id, creator_id=user.id)

    access_token = await get_access_token(async_client, user)

    response = await async_client.get(
        f"/api/shopping-lists/{shopping_list.id}/items/?{urlencode(filter_params)}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == expected_status
    if expected_status != status.HTTP_200_OK:
        assert expected_detail in response.text
