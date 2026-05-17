"""
Attachment Repository
"""
from typing import List
from sqlalchemy.orm import Session
from backend.models.all_models import Attachment
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class AttachmentRepository(BaseRepository[Attachment]):
    """Repository for Attachment entity."""

    def __init__(self, db: Session):
        super().__init__(Attachment, db)

    def get_by_entity(self, entity_type: str, entity_id: int) -> List[Attachment]:
        """Get all attachments for a specific entity."""
        return (
            self.db.query(Attachment)
            .filter(
                (Attachment.entity_type == entity_type) &
                (Attachment.entity_id == entity_id)
            )
            .all()
        )

    def delete_by_entity(self, entity_type: str, entity_id: int) -> int:
        """Delete all attachments for a specific entity. Returns count of deleted attachments."""
        count = self.db.query(Attachment).filter(
            (Attachment.entity_type == entity_type) &
            (Attachment.entity_id == entity_id)
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} attachments for {entity_type} with entity_id={entity_id}")
        return count