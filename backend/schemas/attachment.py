"""
Attachment Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AttachmentBase(BaseModel):
    """Base schema for Attachment."""
    entity_type: str
    entity_id: int
    file_path: str
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    """Schema for creating an Attachment."""
    pass


class AttachmentUpdate(BaseModel):
    """Schema for updating an Attachment."""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None


class AttachmentResponse(AttachmentBase):
    """Schema for Attachment response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime