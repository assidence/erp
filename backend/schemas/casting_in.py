"""
CastingIn Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CastingInBase(BaseModel):
    """Base schema for CastingIn."""
    delivery_note_no: str
    customer_id: int
    foundry_id: int
    casting_id: int
    quantity: Decimal
    incoming_date: datetime
    delivery_date: Optional[datetime] = None
    received_by: Optional[str] = None
    status: Optional[str] = "pending"
    notes: Optional[str] = None
    images: Optional[List[str]] = []


class CastingInCreate(CastingInBase):
    """Schema for creating a CastingIn."""
    pass


class CastingInUpdate(BaseModel):
    """Schema for updating a CastingIn."""
    delivery_note_no: Optional[str] = None
    customer_id: Optional[int] = None
    foundry_id: Optional[int] = None
    casting_id: Optional[int] = None
    quantity: Optional[Decimal] = None
    incoming_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    received_by: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[str]] = None


class CastingInResponse(CastingInBase):
    """Schema for CastingIn response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
