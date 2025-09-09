from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from core.pagination import Paginator
from models.shopping_list_item import ShoppingListItem
from schemas.pagination import Paginated


class ShoppingListItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, shopping_list_item: ShoppingListItem):
        self.session.add(shopping_list_item)
        await self.session.commit()
        await self.session.refresh(shopping_list_item)

        return shopping_list_item

    async def get_all_by_shopping_list_id(
        self,
        shopping_list_id: str,
        paginator: Paginator,
    ) -> Paginated[ShoppingListItem]:
        return await paginator.paginate(
            select(ShoppingListItem).where(
                ShoppingListItem.shopping_list_id == shopping_list_id
            )
        )


def get_shopping_list_item_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShoppingListItemRepository:
    return ShoppingListItemRepository(session)
