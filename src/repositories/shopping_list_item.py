from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from models.shopping_list_item import ShoppingListItem


class ShoppingListItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, shopping_list_item: ShoppingListItem):
        self.session.add(shopping_list_item)
        await self.session.commit()
        await self.session.refresh(shopping_list_item)

        return shopping_list_item


def get_shopping_list_item_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShoppingListItemRepository:
    return ShoppingListItemRepository(session)
