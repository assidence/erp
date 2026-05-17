"""
PaymentPlan Repository
"""
from typing import List
from sqlalchemy.orm import Session
from backend.models.all_models import PaymentPlan
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class PaymentPlanRepository(BaseRepository[PaymentPlan]):
    """Repository for PaymentPlan entity."""

    def __init__(self, db: Session):
        super().__init__(PaymentPlan, db)

    def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[PaymentPlan]:
        """Get all payment plans for a specific customer."""
        return (
            self.db.query(PaymentPlan)
            .filter(PaymentPlan.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[PaymentPlan]:
        """Get payment plans by status."""
        return (
            self.db.query(PaymentPlan)
            .filter(PaymentPlan.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_overdue_payments(self, current_date, skip: int = 0, limit: int = 100) -> List[PaymentPlan]:
        """Get overdue payment plans (expected_date < current_date and not paid)."""
        return (
            self.db.query(PaymentPlan)
            .filter(
                (PaymentPlan.expected_date < current_date) &
                (PaymentPlan.status != "paid")
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_product_out(self, product_out_id: int) -> List[PaymentPlan]:
        """Get all payment plans for a specific product out record."""
        return self.db.query(PaymentPlan).filter(
            PaymentPlan.product_out_id == product_out_id
        ).all()