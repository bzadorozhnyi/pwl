import uuid
from typing import Annotated

from fastapi import Depends

from models.family import FamilyRole
from repositories.family import FamilyRepository, get_family_repository


class FamilyService:
    def __init__(self, family_repository: FamilyRepository):
        self.family_repository = family_repository

    async def is_member(self, family_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.family_repository.is_member(family_id, user_id)

    async def get_user_role(
        self, family_id: uuid.UUID, user_id: uuid.UUID
    ) -> FamilyRole | None:
        return await self.family_repository.get_user_role(family_id, user_id)


def get_family_service(
    family_repository: Annotated[FamilyRepository, Depends(get_family_repository)],
) -> FamilyService:
    return FamilyService(family_repository=family_repository)
