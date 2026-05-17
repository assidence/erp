"""
Common Pydantic Schemas
"""
from typing import Any, List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel):
    """Standard paginated response format."""
    items: List[Any]
    total: int
    page: int
    page_size: int
