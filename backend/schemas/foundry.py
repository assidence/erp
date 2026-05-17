"""
Foundry Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class FoundryBase(BaseModel):
    """Base schema for Foundry."""
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    images: Optional[List[str]] = []


class FoundryCreate(FoundryBase):
    """Schema for creating a Foundry."""
    pass


class FoundryUpdate(BaseModel):
    """Schema for updating a Foundry."""
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    images: Optional[List[str]] = None


class FoundryResponse(FoundryBase):
    """Schema for Foundry response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class FoundryDetailResponse(FoundryResponse):
    """Schema for Foundry with linked customers."""
    linked_customers: List["CustomerSummary"] = []


class CustomerSummary(BaseModel):
    """Minimal Customer summary for embedding in FoundryDetailResponse."""
    id: int
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
