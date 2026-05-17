"""
Casting and CastingDrawing Repositories
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.all_models import Casting, PartDrawing
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class CastingRepository(BaseRepository[Casting]):
    """Repository for Casting entity."""

    def __init__(self, db: Session):
        super().__init__(Casting, db)

    def get_by_part_number(self, part_number: str) -> Optional[Casting]:
        """Get casting by part number."""
        return self.db.query(Casting).filter(Casting.part_number == part_number).first()

    def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[Casting]:
        """Get all castings for a specific customer."""
        return (
            self.db.query(Casting)
            .filter(Casting.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CastingDrawingRepository(BaseRepository[PartDrawing]):
    """Repository for CastingDrawing entity."""

    def __init__(self, db: Session):
        super().__init__(PartDrawing, db)

    def get_by_casting(self, casting_id: int) -> List[PartDrawing]:
        """Get all drawings for a specific casting."""
        return (
            self.db.query(PartDrawing)
            .filter(PartDrawing.casting_id == casting_id)
            .all()
        )