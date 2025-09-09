import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import and_, select

from core.db import get_session
from core.pagination import Paginator
from models.shopping_list_item import ShoppingListItem
from schemas.pagination import Paginated
from schemas.shopping_list_item import ShoppingListItemFilter


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
        filters: ShoppingListItemFilter,
        paginator: Paginator,
    ) -> Paginated[ShoppingListItem]:
        statement = select(ShoppingListItem).where(
            ShoppingListItem.shopping_list_id == shopping_list_id
        )

        if filters.name:
            words = filters.name.split()
            name_conditions = [
                ShoppingListItem.name.ilike(f"%{word}%") for word in words
            ]
            statement = statement.where(and_(*name_conditions))

        if filters.created_from:
            statement = statement.where(
                ShoppingListItem.created_at >= filters.created_from
            )

        if filters.created_to:
            statement = statement.where(
                ShoppingListItem.created_at <= filters.created_to
            )

        return await paginator.paginate(statement)

    async def get_by_id(self, id: uuid.UUID) -> ShoppingListItem | None:
        statement = select(ShoppingListItem).where(ShoppingListItem.id == id)

        return await self.session.scalar(statement)

    async def update(self, shopping_list_item: ShoppingListItem) -> ShoppingListItem:
        shopping_list_item.updated_at = datetime.now()

        self.session.add(shopping_list_item)
        await self.session.commit()
        await self.session.refresh(shopping_list_item)

        return shopping_list_item


def get_shopping_list_item_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ShoppingListItemRepository:
    return ShoppingListItemRepository(session)
