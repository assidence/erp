"""
Attachments API Router
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.all_models import Attachment
from backend.schemas.attachment import AttachmentCreate, AttachmentUpdate, AttachmentResponse
from backend.repositories.attachment import AttachmentRepository
from backend.config import settings, get_logger

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
    """Delete an attachment and its physical file."""
    repo = AttachmentRepository(db)
    attachment = repo.get(attachment_id)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    # Delete physical file
    file_path = Path(attachment.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
            logger.info(f"Deleted physical file: {file_path}")
        except Exception as ex:
            logger.warning(f"Failed to delete physical file {file_path}: {ex}")
    repo.delete(attachment_id)
    logger.info(f"Deleted attachment #{attachment_id}")


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AttachmentResponse])
def get_attachments_by_entity(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    """Get all attachments for a specific entity."""
    repo = AttachmentRepository(db)
    return repo.get_by_entity(entity_type, entity_id)


@router.post("/upload", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a file and create an attachment record.

    - **entity_type**: Type of entity (e.g. 'castings', 'production_plans', 'payment_plans')
    - **entity_id**: ID of the entity
    - **description**: Optional description of the file
    - **file**: The file to upload (image, PDF, etc.)
    """
    # 1. Ensure upload directory exists
    upload_dir = settings.UPLOAD_DIR / entity_type / str(entity_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 2. Determine safe filename
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / safe_name

    # 3. Read and save file content
    content = await file.read()
    file_path.write_bytes(content)
    logger.info(f"Saved file: {file_path} ({len(content)} bytes)")

    # 4. Create attachment record
    repo = AttachmentRepository(db)
    att = Attachment(
        entity_type=entity_type,
        entity_id=entity_id,
        file_path=str(file_path),
        file_name=file.filename or "unknown",
        file_size=len(content),
        mime_type=file.content_type or "application/octet-stream",
        description=description,
    )
    result = repo.create(att)
    logger.info(f"Created attachment record id={result.id} for {entity_type}#{entity_id}")
    return result
