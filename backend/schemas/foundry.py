"""
Foundry Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class FoundryBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    images: Optional[List[str]] = []


class FoundryCreate(FoundryBase):
    pass


class FoundryUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    images: Optional[List[str]] = None


class FoundryResponse(FoundryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CustomerSummary(BaseModel):
    id: int
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class FoundryDetailResponse(FoundryResponse):
    linked_customers: List[CustomerSummary] = []
