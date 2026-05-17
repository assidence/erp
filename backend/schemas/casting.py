"""
Casting and CastingDrawing Pydantic Schemas (renamed from part)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# Casting Schemas
class CastingBase(BaseModel):
    """Base schema for Casting."""
    customer_id: int
    part_number: str
    name: str
    description: Optional[str] = None
    latest_price: Optional[Decimal] = None
    images: Optional[list[str]] = []


class CastingCreate(CastingBase):
    """Schema for creating a Casting."""
    pass


class CastingUpdate(BaseModel):
    """Schema for updating a Casting."""
    customer_id: Optional[int] = None
    part_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    latest_price: Optional[Decimal] = None
    images: Optional[list[str]] = None


class CastingResponse(CastingBase):
    """Schema for Casting response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# CastingDrawing Schemas
class CastingDrawingBase(BaseModel):
    """Base schema for CastingDrawing."""
    casting_id: int
    version: str
    update_date: Optional[datetime] = None
    file_path: Optional[str] = None
    notes: Optional[str] = None


class CastingDrawingCreate(CastingDrawingBase):
    """Schema for creating a CastingDrawing."""
    pass


class CastingDrawingUpdate(BaseModel):
    """Schema for updating a CastingDrawing."""
    casting_id: Optional[int] = None
    version: Optional[str] = None
    update_date: Optional[datetime] = None
    file_path: Optional[str] = None
    notes: Optional[str] = None


class CastingDrawingResponse(CastingDrawingBase):
    """Schema for CastingDrawing response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
