"""
Customer Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    """Base schema for Customer."""
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment_terms: Optional[str] = None
    payment_days: Optional[int] = None
    address: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a Customer."""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a Customer."""
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment_terms: Optional[str] = None
    payment_days: Optional[int] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for Customer response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CustomerDetailResponse(CustomerResponse):
    """Schema for Customer with related data."""
    linked_foundries: List["FoundrySummary"] = []
    linked_castings: List["CastingSummary"] = []


class FoundrySummary(BaseModel):
    """Minimal Foundry summary for embedding in CustomerDetailResponse."""
    id: int
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CastingSummary(BaseModel):
    """Minimal Casting summary for embedding in CustomerDetailResponse."""
    id: int
    part_number: str
    name: str

    model_config = ConfigDict(from_attributes=True)
