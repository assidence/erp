"""
Castings API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.all_models import Casting
from backend.schemas.casting import CastingCreate, CastingUpdate, CastingResponse
from backend.schemas.common import PaginatedResponse
from backend.repositories.casting import CastingRepository
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/castings", tags=["castings"])


@router.get("/", )
def list_castings(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all castings with pagination and optional search."""
    skip = (page - 1) * page_size
    query = db.query(Casting)

    if search:
        query = query.filter(
            (Casting.name.contains(search)) | (Casting.part_number.contains(search))
        )

    total = query.count()
    items = query.offset(skip).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{casting_id}", response_model=CastingResponse)
def get_casting(casting_id: int, db: Session = Depends(get_db)):
    """Get a casting by ID."""
    casting = db.query(Casting).filter(Casting.id == casting_id).first()
    if not casting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Casting not found")
    return casting


@router.post("/", response_model=CastingResponse, status_code=status.HTTP_201_CREATED)
def create_casting(data: CastingCreate, db: Session = Depends(get_db)):
    """Create a new casting."""
    casting = Casting(**data.model_dump())
    db.add(casting)
    db.commit()
    db.refresh(casting)
    logger.info(f"Created casting id={casting.id}")
    return casting


@router.put("/{casting_id}", response_model=CastingResponse)
def update_casting(casting_id: int, data: CastingUpdate, db: Session = Depends(get_db)):
    """Update a casting."""
    casting = db.query(Casting).filter(Casting.id == casting_id).first()
    if not casting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Casting not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(casting, key):
            setattr(casting, key, value)
    db.commit()
    db.refresh(casting)
    logger.info(f"Updated casting id={casting_id}")
    return casting


@router.delete("/{casting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_casting(casting_id: int, db: Session = Depends(get_db)):
    """Delete a casting."""
    casting = db.query(Casting).filter(Casting.id == casting_id).first()
    if not casting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Casting not found")
    db.delete(casting)
    db.commit()
    logger.info(f"Deleted casting id={casting_id}")
