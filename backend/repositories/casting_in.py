"""
CastingIn Repository
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.all_models import CastingIn
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class CastingInRepository(BaseRepository[CastingIn]):
    """Repository for CastingIn entity."""

    def __init__(self, db: Session):
        super().__init__(CastingIn, db)

    def get_by_delivery_note_no(self, delivery_note_no: str) -> Optional[CastingIn]:
        """Get casting inbound record by delivery note number."""
        return self.db.query(CastingIn).filter(CastingIn.delivery_note_no == delivery_note_no).first()

    def get_by_foundry(self, foundry_id: int, skip: int = 0, limit: int = 100) -> List[CastingIn]:
        """Get all inbound records for a specific foundry."""
        return (
            self.db.query(CastingIn)
            .filter(CastingIn.foundry_id == foundry_id)
            .order_by(CastingIn.incoming_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_casting(self, casting_id: int, skip: int = 0, limit: int = 100) -> List[CastingIn]:
        """Get all inbound records for a specific casting."""
        return (
            self.db.query(CastingIn)
            .filter(CastingIn.casting_id == casting_id)
            .order_by(CastingIn.incoming_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )