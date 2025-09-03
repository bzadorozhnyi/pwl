import pytest


@pytest.mark.anyio
async def test_family_task_factory(
    family_task_factory,
    family_task_create_payload_factory,
    family_task_update_payload_factory,
):
    family_task_factory()
    family_task_create_payload_factory()
    family_task_update_payload_factory()
