import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from models.family import Family, FamilyMember, FamilyRole


class FamilyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self):
        family = Family()

        self.session.add(family)
        await self.session.commit()
        await self.session.refresh(family)

        return family

    async def add_member(
        self,
        family_id: uuid.UUID,
        user_id: uuid.UUID,
        role: FamilyRole = FamilyRole.MEMBER,
    ):
        family_member = FamilyMember(family_id=family_id, user_id=user_id, role=role)

        self.session.add(family_member)
        await self.session.commit()
        await self.session.refresh(family_member)

        return family_member

    async def is_member(self, family_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        statement = select(FamilyMember).where(
            FamilyMember.family_id == family_id, FamilyMember.user_id == user_id
        )
        result = await self.session.execute(statement)

        return result.scalar() is not None

    async def get_user_role(
        self, family_id: uuid.UUID, user_id: uuid.UUID
    ) -> FamilyRole | None:
        statement = select(FamilyMember.role).where(
            FamilyMember.family_id == family_id, FamilyMember.user_id == user_id
        )
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_user_families(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        statement = select(FamilyMember.family_id).where(
            FamilyMember.user_id == user_id
        )
        result = await self.session.execute(statement)

        return result.scalars().all()


def get_family_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FamilyRepository:
    return FamilyRepository(session)
