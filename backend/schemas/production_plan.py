"""
ProductionPlan Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ProductionPlanItem Schemas
class ProductionPlanItemBase(BaseModel):
    """Base schema for ProductionPlanItem."""
    casting_id: int
    required_quantity: Decimal
    produced_quantity: Optional[Decimal] = Decimal("0")
    unit_price: Optional[Decimal] = None
    remaining_quantity: Optional[Decimal] = Decimal("0")


class ProductionPlanItemCreate(ProductionPlanItemBase):
    """Schema for creating a ProductionPlanItem."""
    pass


class ProductionPlanItemUpdate(BaseModel):
    """Schema for updating a ProductionPlanItem."""
    casting_id: Optional[int] = None
    required_quantity: Optional[Decimal] = None
    produced_quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None


class ProductionPlanItemResponse(ProductionPlanItemBase):
    """Schema for ProductionPlanItem response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int


# ProductionPlan Schemas
class ProductionPlanBase(BaseModel):
    """Base schema for ProductionPlan."""
    plan_no: Optional[str] = None
    customer_id: int
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = "pending"
    notes: Optional[str] = None
    images: Optional[list[str]] = []


class ProductionPlanCreate(ProductionPlanBase):
    """Schema for creating a ProductionPlan with items."""
    items: List[ProductionPlanItemCreate]


class ProductionPlanUpdate(BaseModel):
    """Schema for updating a ProductionPlan."""
    plan_no: Optional[str] = None
    customer_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[list[str]] = None
    items: Optional[List[ProductionPlanItemCreate]] = None


class ProductionPlanResponse(ProductionPlanBase):
    """Schema for ProductionPlan response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    images: list[str] = []
    items: List[ProductionPlanItemResponse] = []
