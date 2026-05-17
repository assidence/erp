"""
PaymentPlan Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PaymentPlanBase(BaseModel):
    """Base schema for PaymentPlan."""
    customer_id: int
    workpiece_out_id: int
    expected_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    amount: Decimal
    status: Optional[str] = "pending"
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class PaymentPlanCreate(PaymentPlanBase):
    pass


class PaymentPlanUpdate(BaseModel):
    customer_id: Optional[int] = None
    workpiece_out_id: Optional[int] = None
    expected_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    amount: Optional[Decimal] = None
    status: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class PaymentPlanResponse(PaymentPlanBase):
    """Schema for PaymentPlan response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime