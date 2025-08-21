import pytest


@pytest.mark.anyio
async def test_user_factories(user_factory, user_create_payload_factory):
    user_factory()
    user_create_payload_factory()
