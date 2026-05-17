"""
WorkpieceOut Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class WorkpieceOutItemBase(BaseModel):
    """Base schema for WorkpieceOutItem."""
    production_plan_item_id: int
    casting_id: int
    quantity: Decimal
    unit_price: Optional[Decimal] = None


class WorkpieceOutItemCreate(WorkpieceOutItemBase):
    pass


class WorkpieceOutItemUpdate(BaseModel):
    production_plan_item_id: Optional[int] = None
    casting_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None


class WorkpieceOutItemResponse(WorkpieceOutItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    workpiece_out_id: int


class WorkpieceOutBase(BaseModel):
    """Base schema for WorkpieceOut (送货单表头)."""
    delivery_note_no: str
    production_plan_id: int
    customer_id: int
    delivery_date: Optional[datetime] = None
    shipping_address: Optional[str] = None
    status: Optional[str] = "pending"
    notes: Optional[str] = None
    images: Optional[List[str]] = []


class WorkpieceOutCreate(WorkpieceOutBase):
    """Schema for creating a WorkpieceOut with items."""
    items: List[WorkpieceOutItemCreate]


class WorkpieceOutUpdate(BaseModel):
    """Schema for updating a WorkpieceOut."""
    delivery_note_no: Optional[str] = None
    production_plan_id: Optional[int] = None
    customer_id: Optional[int] = None
    delivery_date: Optional[datetime] = None
    shipping_address: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[str]] = None
    items: Optional[List[WorkpieceOutItemCreate]] = None


class WorkpieceOutResponse(WorkpieceOutBase):
    """Schema for WorkpieceOut response."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[str] = []
    items: List[WorkpieceOutItemResponse] = []
