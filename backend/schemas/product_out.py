"""
ProductOut Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductOutBase(BaseModel):
    """Base schema for ProductOut."""
    delivery_note_no: str
    customer_id: int
    part_id: int
    quantity: Decimal
    unit_price: Decimal
    delivery_date: Optional[datetime] = None
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[list[str]] = []


class ProductOutCreate(ProductOutBase):
    """Schema for creating a ProductOut."""
    pass


class ProductOutUpdate(BaseModel):
    """Schema for updating a ProductOut."""
    delivery_note_no: Optional[str] = None
    customer_id: Optional[int] = None
    part_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    delivery_date: Optional[datetime] = None
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[list[str]] = None


class ProductOutResponse(ProductOutBase):
    """Schema for ProductOut response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    images: list[str] = []