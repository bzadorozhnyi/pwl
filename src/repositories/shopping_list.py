import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from core.pagination import Paginator
from models.shopping_list import ShoppingList
from schemas.pagination import Paginated


class ShoppingListRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, shopping_list: ShoppingList):
        self.session.add(shopping_list)
        await self.session.commit()
        await self.session.refresh(shopping_list)

        return shopping_list

    async def list_by_family_id(
        self, family_id: uuid.UUID, paginator: Paginator
    ) -> Paginated[ShoppingList]:
        return await paginator.paginate(
            select(ShoppingList).where(ShoppingList.family_id == family_id)
        )


def get_shopping_list_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShoppingListRepository:
    return ShoppingListRepository(session)
