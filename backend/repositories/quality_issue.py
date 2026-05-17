"""
QualityIssue Repository
"""
from typing import List
from sqlalchemy.orm import Session
from backend.models.all_models import QualityIssue
from backend.repositories.base import BaseRepository
from backend.config import get_logger

logger = get_logger(__name__)


class QualityIssueRepository(BaseRepository[QualityIssue]):
    """Repository for QualityIssue entity."""

    def __init__(self, db: Session):
        super().__init__(QualityIssue, db)

    def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[QualityIssue]:
        """Get all quality issues for a specific customer."""
        return (
            self.db.query(QualityIssue)
            .filter(QualityIssue.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[QualityIssue]:
        """Get quality issues by status."""
        return (
            self.db.query(QualityIssue)
            .filter(QualityIssue.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_severity(self, severity: str, skip: int = 0, limit: int = 100) -> List[QualityIssue]:
        """Get quality issues by severity."""
        return (
            self.db.query(QualityIssue)
            .filter(QualityIssue.severity == severity)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_open_issues(self, skip: int = 0, limit: int = 100) -> List[QualityIssue]:
        """Get all open (not resolved) quality issues."""
        return (
            self.db.query(QualityIssue)
            .filter(QualityIssue.status != "resolved")
            .offset(skip)
            .limit(limit)
            .all()
        )