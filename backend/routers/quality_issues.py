"""
QualityIssues API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.all_models import QualityIssue
from backend.schemas.quality_issue import QualityIssueCreate, QualityIssueUpdate, QualityIssueResponse
from backend.schemas.common import PaginatedResponse
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/quality-issues", tags=["quality-issues"])


@router.get("/", )
def list_quality_issues(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all quality issues with pagination."""
    skip = (page - 1) * page_size
    query = db.query(QualityIssue)

    if search:
        query = query.filter(QualityIssue.description.contains(search))

    total = query.count()
    items = query.order_by(QualityIssue.created_at.desc()).offset(skip).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{issue_id}", response_model=QualityIssueResponse)
def get_quality_issue(issue_id: int, db: Session = Depends(get_db)):
    """Get a quality issue by ID."""
    issue = db.query(QualityIssue).filter(QualityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QualityIssue not found")
    return issue


@router.post("/", response_model=QualityIssueResponse, status_code=status.HTTP_201_CREATED)
def create_quality_issue(data: QualityIssueCreate, db: Session = Depends(get_db)):
    """Create a new quality issue."""
    issue = QualityIssue(**data.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    logger.info(f"Created quality_issue id={issue.id}")
    return issue


@router.put("/{issue_id}", response_model=QualityIssueResponse)
def update_quality_issue(issue_id: int, data: QualityIssueUpdate, db: Session = Depends(get_db)):
    """Update a quality issue."""
    issue = db.query(QualityIssue).filter(QualityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QualityIssue not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(issue, key):
            setattr(issue, key, value)
    db.commit()
    db.refresh(issue)
    logger.info(f"Updated quality_issue id={issue_id}")
    return issue


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quality_issue(issue_id: int, db: Session = Depends(get_db)):
    """Delete a quality issue."""
    issue = db.query(QualityIssue).filter(QualityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QualityIssue not found")
    db.delete(issue)
    db.commit()
    logger.info(f"Deleted quality_issue id={issue_id}")


@router.get("/customer/{customer_id}", response_model=list)
def get_quality_issues_by_customer(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all quality issues for a specific customer."""
    issues = db.query(QualityIssue).filter(QualityIssue.customer_id == customer_id).offset(skip).limit(limit).all()
    return issues


@router.get("/status/{status}", response_model=list)
def get_quality_issues_by_status(status: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get quality issues by status."""
    issues = db.query(QualityIssue).filter(QualityIssue.status == status).offset(skip).limit(limit).all()
    return issues


@router.get("/severity/{severity}", response_model=list)
def get_quality_issues_by_severity(severity: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get quality issues by severity."""
    issues = db.query(QualityIssue).filter(QualityIssue.severity == severity).offset(skip).limit(limit).all()
    return issues
