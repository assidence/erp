"""
Attachments API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.all_models import Attachment
from backend.schemas.attachment import AttachmentCreate, AttachmentUpdate, AttachmentResponse
from backend.repositories.attachment import AttachmentRepository
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/attachments", tags=["attachments"])


@router.get("/", response_model=List[AttachmentResponse])
def list_attachments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all attachments with pagination."""
    repo = AttachmentRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{attachment_id}", response_model=AttachmentResponse)
def get_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Get an attachment by ID."""
    repo = AttachmentRepository(db)
    attachment = repo.get(attachment_id)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return attachment


@router.post("/", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
def create_attachment(data: AttachmentCreate, db: Session = Depends(get_db)):
    """Create a new attachment record."""
    repo = AttachmentRepository(db)
    attachment = Attachment(**data.model_dump())
    return repo.create(attachment)


@router.put("/{attachment_id}", response_model=AttachmentResponse)
def update_attachment(attachment_id: int, data: AttachmentUpdate, db: Session = Depends(get_db)):
    """Update an attachment."""
    repo = AttachmentRepository(db)
    if not repo.exists(attachment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return repo.update(attachment_id, data.model_dump(exclude_unset=True))


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    """Delete an attachment."""
    repo = AttachmentRepository(db)
    if not repo.delete(attachment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AttachmentResponse])
def get_attachments_by_entity(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    """Get all attachments for a specific entity."""
    repo = AttachmentRepository(db)
    return repo.get_by_entity(entity_type, entity_id)