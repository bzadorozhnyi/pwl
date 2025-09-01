import pytest


@pytest.mark.anyio
async def test_family_factory(family_factory, family_member_factory):
    family_factory()
    family_member_factory()
