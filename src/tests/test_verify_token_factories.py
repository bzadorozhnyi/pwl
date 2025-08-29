import pytest


@pytest.mark.anyio
async def test_verify_token_factory(verify_token_factory):
    verify_token_factory()
