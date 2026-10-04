from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """
    Standard pagination envelope returned by list endpoints.
    """

    items: list[T]
    total: int = Field(
        description="Total number of records matching the filters",
    )
    skip: int
    limit: int
