"""
QualityIssue Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class QualityIssueBase(BaseModel):
    """Base schema for QualityIssue."""
    customer_id: int
    workpiece_out_id: Optional[int] = None
    casting_id: int
    issue_type: str
    description: str
    severity: Optional[str] = "medium"
    status: Optional[str] = "open"
    resolution: Optional[str] = None
    notes: Optional[str] = None
    issue_date: Optional[datetime] = None


class QualityIssueCreate(QualityIssueBase):
    """Schema for creating a QualityIssue."""
    pass


class QualityIssueUpdate(BaseModel):
    """Schema for updating a QualityIssue."""
    customer_id: Optional[int] = None
    workpiece_out_id: Optional[int] = None
    casting_id: Optional[int] = None
    issue_type: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    resolution: Optional[str] = None
    notes: Optional[str] = None
    issue_date: Optional[datetime] = None


class QualityIssueResponse(QualityIssueBase):
    """Schema for QualityIssue response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
