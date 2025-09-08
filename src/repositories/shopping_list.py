from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from models.shopping_list import ShoppingList


class ShoppingListRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, shopping_list: ShoppingList):
        self.session.add(shopping_list)
        await self.session.commit()
        await self.session.refresh(shopping_list)

        return shopping_list


def get_shopping_list_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShoppingListRepository:
    return ShoppingListRepository(session)
