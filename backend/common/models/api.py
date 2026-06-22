from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: T


class PagedResult(BaseModel, Generic[T]):
    list: list[T]
    total: int
    page: int
    size: int
