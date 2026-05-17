"""
Customer Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.all_models import Customer
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer entity."""

    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def get_by_name(self, name: str) -> Optional[Customer]:
        """Get customer by name."""
        return self.db.query(Customer).filter(Customer.name == name).first()

    def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone number."""
        return self.db.query(Customer).filter(Customer.phone == phone).first()

    def search(self, keyword: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Search customers by name or contact person."""
        query = self.db.query(Customer).filter(
            (Customer.name.contains(keyword)) | (Customer.contact_person.contains(keyword))
        )
        return query.offset(skip).limit(limit).all()

    def get_with_relations(self, id: int) -> Optional[Customer]:
        """Get customer with all related data."""
        return (
            self.db.query(Customer)
            .filter(Customer.id == id)
            .first()
        )