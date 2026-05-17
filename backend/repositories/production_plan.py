"""
ProductionPlan Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.all_models import ProductionPlan
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class ProductionPlanRepository(BaseRepository[ProductionPlan]):
    """Repository for ProductionPlan entity."""

    def __init__(self, db: Session):
        super().__init__(ProductionPlan, db)

    def get_by_plan_no(self, plan_no: str) -> Optional[ProductionPlan]:
        """Get production plan by plan number."""
        return self.db.query(ProductionPlan).filter(ProductionPlan.plan_no == plan_no).first()

    def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[ProductionPlan]:
        """Get all production plans for a specific customer."""
        return (
            self.db.query(ProductionPlan)
            .filter(ProductionPlan.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[ProductionPlan]:
        """Get production plans by status."""
        return (
            self.db.query(ProductionPlan)
            .filter(ProductionPlan.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_overdue_plans(self, current_date, skip: int = 0, limit: int = 100) -> List[ProductionPlan]:
        """Get overdue production plans (due_date < current_date and not completed)."""
        return (
            self.db.query(ProductionPlan)
            .filter(
                (ProductionPlan.due_date < current_date) &
                (ProductionPlan.status != "completed")
            )
            .offset(skip)
            .limit(limit)
            .all()
        )