from typing import Generic

from pydantic import BaseModel
from typing_extensions import TypeVar

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    count: int
    next_page: str | None
    previous_page: str | None
    results: list[T]
