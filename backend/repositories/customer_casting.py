"""
CustomerCasting Junction Table Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models.all_models import CustomerCasting, Casting
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class CustomerCastingRepository(BaseRepository[CustomerCasting]):
    """Repository for Customer-Casting junction table."""

    def __init__(self, db: Session):
        super().__init__(CustomerCasting, db)

    def link(self, customer_id: int, casting_id: int) -> Optional[CustomerCasting]:
        """Link a casting to a customer."""
        # Check if link already exists
        existing = self.get_link(customer_id, casting_id)
        if existing:
            logger.info(f"Customer-Casting link already exists: customer={customer_id}, casting={casting_id}")
            return existing

        link = CustomerCasting(customer_id=customer_id, casting_id=casting_id)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        logger.info(f"Linked casting {casting_id} to customer {customer_id}")
        return link

    def unlink(self, customer_id: int, casting_id: int) -> bool:
        """Unlink a casting from a customer."""
        link = self.get_link(customer_id, casting_id)
        if link:
            self.db.delete(link)
            self.db.commit()
            logger.info(f"Unlinked casting {casting_id} from customer {customer_id}")
            return True
        return False

    def get_link(self, customer_id: int, casting_id: int) -> Optional[CustomerCasting]:
        """Get a specific link."""
        return (
            self.db.query(CustomerCasting)
            .filter(
                and_(
                    CustomerCasting.customer_id == customer_id,
                    CustomerCasting.casting_id == casting_id
                )
            )
            .first()
        )

    def get_castings_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[Casting]:
        """Get all castings linked to a specific customer."""
        results = (
            self.db.query(CustomerCasting)
            .filter(CustomerCasting.customer_id == customer_id)
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

    def is_linked(self, customer_id: int, casting_id: int) -> bool:
        """Check if a casting is linked to a customer."""
        return self.get_link(customer_id, casting_id) is not None