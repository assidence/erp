"""
CustomerFoundry Junction Table Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models.all_models import CustomerFoundry, Foundry
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class CustomerFoundryRepository(BaseRepository[CustomerFoundry]):
    """Repository for Customer-Foundry junction table."""

    def __init__(self, db: Session):
        super().__init__(CustomerFoundry, db)

    def link(self, customer_id: int, foundry_id: int) -> Optional[CustomerFoundry]:
        """Link a foundry to a customer."""
        # Check if link already exists
        existing = self.get_link(customer_id, foundry_id)
        if existing:
            logger.info(f"Customer-Foundry link already exists: customer={customer_id}, foundry={foundry_id}")
            return existing

        link = CustomerFoundry(customer_id=customer_id, foundry_id=foundry_id)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        logger.info(f"Linked foundry {foundry_id} to customer {customer_id}")
        return link

    def unlink(self, customer_id: int, foundry_id: int) -> bool:
        """Unlink a foundry from a customer."""
        link = self.get_link(customer_id, foundry_id)
        if link:
            self.db.delete(link)
            self.db.commit()
            logger.info(f"Unlinked foundry {foundry_id} from customer {customer_id}")
            return True
        return False

    def get_link(self, customer_id: int, foundry_id: int) -> Optional[CustomerFoundry]:
        """Get a specific link."""
        return (
            self.db.query(CustomerFoundry)
            .filter(
                and_(
                    CustomerFoundry.customer_id == customer_id,
                    CustomerFoundry.foundry_id == foundry_id
                )
            )
            .first()
        )

    def get_foundries_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[Foundry]:
        """Get all foundries linked to a specific customer."""
        results = (
            self.db.query(CustomerFoundry)
            .filter(CustomerFoundry.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        foundry_ids = [r.foundry_id for r in results]
        if not foundry_ids:
            return []
        return (
            self.db.query(Foundry)
            .filter(Foundry.id.in_(foundry_ids))
            .all()
        )

    def get_customers_by_foundry(self, foundry_id: int, skip: int = 0, limit: int = 100) -> List:
        """Get all customers linked to a specific foundry."""
        return (
            self.db.query(CustomerFoundry)
            .filter(CustomerFoundry.foundry_id == foundry_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def is_linked(self, customer_id: int, foundry_id: int) -> bool:
        """Check if a foundry is linked to a customer."""
        return self.get_link(customer_id, foundry_id) is not None