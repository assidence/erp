"""
WorkpieceOut Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.all_models import WorkpieceOut
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class WorkpieceOutRepository(BaseRepository[WorkpieceOut]):
    """Repository for WorkpieceOut entity."""

    def __init__(self, db: Session):
        super().__init__(WorkpieceOut, db)

    def get_by_delivery_note_no(self, delivery_note_no: str) -> Optional[WorkpieceOut]:
        """Get workpiece outbound record by delivery note number."""
        return self.db.query(WorkpieceOut).filter(WorkpieceOut.delivery_note_no == delivery_note_no).first()

    def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[WorkpieceOut]:
        """Get all outbound records for a specific customer."""
        return (
            self.db.query(WorkpieceOut)
            .filter(WorkpieceOut.customer_id == customer_id)
            .order_by(WorkpieceOut.delivery_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_casting(self, casting_id: int, skip: int = 0, limit: int = 100) -> List[WorkpieceOut]:
        """Get all outbound records for a specific casting."""
        return (
            self.db.query(WorkpieceOut)
            .filter(WorkpieceOut.casting_id == casting_id)
            .order_by(WorkpieceOut.delivery_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )