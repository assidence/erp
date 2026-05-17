"""
MaterialIn Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MaterialInBase(BaseModel):
    """Base schema for MaterialIn."""
    delivery_note_no: str
    supplier_id: int
    part_id: int
    quantity: Decimal
    unit_price: Decimal
    incoming_date: datetime
    delivery_date: Optional[datetime] = None
    received_by: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[list[str]] = []


class MaterialInCreate(MaterialInBase):
    """Schema for creating a MaterialIn."""
    pass


class MaterialInUpdate(BaseModel):
    """Schema for updating a MaterialIn."""
    delivery_note_no: Optional[str] = None
    supplier_id: Optional[int] = None
    part_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    incoming_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    received_by: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[list[str]] = None


class MaterialInResponse(MaterialInBase):
    """Schema for MaterialIn response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    images: list[str] = []