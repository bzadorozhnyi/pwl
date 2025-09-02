from typing import Annotated

from fastapi import Depends, Request
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from core.pagination import Paginator


def get_paginator(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> Paginator:
    base_url = str(request.url).split("?")[0]
    return Paginator(session=session, base_url=base_url, page=page, page_size=page_size)
