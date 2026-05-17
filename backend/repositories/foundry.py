"""
Foundry Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.all_models import Foundry
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class FoundryRepository(BaseRepository[Foundry]):
    """Repository for Foundry entity."""

    def __init__(self, db: Session):
        super().__init__(Foundry, db)

    def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[Foundry]:
        """Get all foundries for a specific customer."""
        return (
            self.db.query(Foundry)
            .filter(Foundry.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name(self, name: str) -> Optional[Foundry]:
        """Get foundry by name."""
        return self.db.query(Foundry).filter(Foundry.name == name).first()