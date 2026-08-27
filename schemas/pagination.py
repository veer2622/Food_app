from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    page: int
    limit: int
    total_query: int
    total_page: int
    data: list[T]