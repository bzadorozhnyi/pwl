from urllib.parse import urlencode

from sqlalchemy import Executable, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from schemas.pagination import Paginated


class Paginator:
    def __init__(
        self,
        session: AsyncSession,
        base_url: str,
        page: int,
        page_size: int,
        query_params: dict,
    ):
        self.session = session
        self.base_url = base_url
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.query_params = query_params

    def build_url(self, page: int) -> str:
        params = dict(self.query_params)
        params["page"] = page
        params["page_size"] = self.page_size

        return f"{self.base_url}?{urlencode(params)}"

    def get_next_page(self, total_count: int) -> str:
        if self.page * self.page_size < total_count:
            return self.build_url(self.page + 1)

        return None

    def get_previous_page(self) -> str:
        if self.page > 1:
            return self.build_url(self.page - 1)

        return None

    async def get_total_count(self, statement: Executable) -> int:
        count_stmt = select(func.count()).select_from(statement.subquery())
        result = await self.session.execute(count_stmt)

        return result.scalar_one()

    async def paginate(self, statement: Executable) -> Paginated:
        total_count = await self.get_total_count(statement)
        result = await self.session.execute(
            statement.offset(self.offset).limit(self.page_size)
        )

        return Paginated(
            count=total_count,
            next_page=self.get_next_page(total_count),
            previous_page=self.get_previous_page(),
            results=result.scalars().all(),
        )
