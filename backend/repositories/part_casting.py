"""
PartCasting Junction Table Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models.all_models import PartCasting, Casting, Part
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class PartCastingRepository(BaseRepository[PartCasting]):
    """Repository for Part-Casting junction table."""

    def __init__(self, db: Session):
        super().__init__(PartCasting, db)

    def link(self, part_id: int, casting_id: int) -> Optional[PartCasting]:
        """Link a casting to a part."""
        # Check if link already exists
        existing = self.get_link(part_id, casting_id)
        if existing:
            logger.info(f"Part-Casting link already exists: part={part_id}, casting={casting_id}")
            return existing

        link = PartCasting(part_id=part_id, casting_id=casting_id)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        logger.info(f"Linked casting {casting_id} to part {part_id}")
        return link

    def unlink(self, part_id: int, casting_id: int) -> bool:
        """Unlink a casting from a part."""
        link = self.get_link(part_id, casting_id)
        if link:
            self.db.delete(link)
            self.db.commit()
            logger.info(f"Unlinked casting {casting_id} from part {part_id}")
            return True
        return False

    def get_link(self, part_id: int, casting_id: int) -> Optional[PartCasting]:
        """Get a specific link."""
        return (
            self.db.query(PartCasting)
            .filter(
                and_(
                    PartCasting.part_id == part_id,
                    PartCasting.casting_id == casting_id
                )
            )
            .first()
        )

    def get_castings_by_part(self, part_id: int, skip: int = 0, limit: int = 100) -> List[Casting]:
        """Get all castings linked to a specific part."""
        results = (
            self.db.query(PartCasting)
            .filter(PartCasting.part_id == part_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        casting_ids = [r.casting_id for r in results]
        if not casting_ids:
            return []
        return (
            self.db.query(Casting)
            .filter(Casting.id.in_(casting_ids))
            .all()
        )

    def get_parts_by_casting(self, casting_id: int, skip: int = 0, limit: int = 100) -> List[Part]:
        """Get all parts linked to a specific casting."""
        results = (
            self.db.query(PartCasting)
            .filter(PartCasting.casting_id == casting_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        part_ids = [r.part_id for r in results]
        if not part_ids:
            return []
        return (
            self.db.query(Part)
            .filter(Part.id.in_(part_ids))
            .all()
        )

    def is_linked(self, part_id: int, casting_id: int) -> bool:
        """Check if a casting is linked to a part."""
        return self.get_link(part_id, casting_id) is not None