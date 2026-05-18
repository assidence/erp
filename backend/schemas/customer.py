"""
Customer Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
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
    pass


class CustomerUpdate(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class FoundrySummary(BaseModel):
    id: int
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CastingSummary(BaseModel):
    id: int
    part_number: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class CustomerDetailResponse(CustomerResponse):
    linked_foundries: List["FoundrySummary"] = []
    linked_castings: List["CastingSummary"] = []
