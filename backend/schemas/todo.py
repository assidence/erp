"""
Todo Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TodoBase(BaseModel):
    content: str
    is_done: Optional[bool] = False
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    content: Optional[str] = None
    is_done: Optional[bool] = None
    due_date: Optional[datetime] = None


class TodoResponse(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
