"""
CastingIns API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend.models.all_models import CastingIn, Foundry, Casting
from backend.schemas.casting_in import CastingInCreate, CastingInUpdate, CastingInResponse
from backend.schemas.common import PaginatedResponse
from backend.repositories.casting_in import CastingInRepository
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/casting-ins", tags=["casting-ins"])


@router.get("/", )
def list_casting_ins(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all casting inbound records with pagination."""
    skip = (page - 1) * page_size
    query = db.query(CastingIn)

    if search:
        query = query.filter(CastingIn.delivery_note_no.contains(search))

    total = query.count()
    items = query.order_by(CastingIn.created_at.desc()).offset(skip).limit(page_size).all()

    # Enrich with foundry and casting names
    result = []
    for item in items:
        foundry = db.query(Foundry).filter(Foundry.id == item.foundry_id).first()
        casting = db.query(Casting).filter(Casting.id == item.casting_id).first()
        resp = {**CastingInResponse.model_validate(item).model_dump()}
        resp["foundry_name"] = foundry.name if foundry else None
        resp["foundry_contact"] = foundry.contact_person if foundry else None
        resp["foundry_phone"] = foundry.phone if foundry else None
        resp["casting_name"] = casting.name if casting else None
        resp["casting_part_number"] = casting.part_number if casting else None
        result.append(resp)

    return {"items": result, "total": total, "page": page, "page_size": page_size}


@router.get("/{casting_in_id}")
def get_casting_in(casting_in_id: int, db: Session = Depends(get_db)):
    """Get a casting inbound record by ID."""
    record = db.query(CastingIn).filter(CastingIn.id == casting_in_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CastingIn not found")
    foundry = db.query(Foundry).filter(Foundry.id == record.foundry_id).first()
    casting = db.query(Casting).filter(Casting.id == record.casting_id).first()
    resp = {**CastingInResponse.model_validate(record).model_dump()}
    resp["foundry_name"] = foundry.name if foundry else None
    resp["foundry_contact"] = foundry.contact_person if foundry else None
    resp["foundry_phone"] = foundry.phone if foundry else None
    resp["casting_name"] = casting.name if casting else None
    resp["casting_part_number"] = casting.part_number if casting else None
    return resp


@router.post("/", response_model=CastingInResponse, status_code=status.HTTP_201_CREATED)
def create_casting_in(data: CastingInCreate, db: Session = Depends(get_db)):
    """Create a new casting inbound record."""
    existing = db.query(CastingIn).filter(CastingIn.delivery_note_no == data.delivery_note_no).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Delivery note '{data.delivery_note_no}' already exists")
    record = CastingIn(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Created casting_in id={record.id}")
    return record


@router.put("/{casting_in_id}", response_model=CastingInResponse)
def update_casting_in(casting_in_id: int, data: CastingInUpdate, db: Session = Depends(get_db)):
    """Update a casting inbound record."""
    record = db.query(CastingIn).filter(CastingIn.id == casting_in_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CastingIn not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(record, key):
            setattr(record, key, value)
    db.commit()
    db.refresh(record)
    logger.info(f"Updated casting_in id={casting_in_id}")
    return record


@router.delete("/{casting_in_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_casting_in(casting_in_id: int, db: Session = Depends(get_db)):
    """Delete a casting inbound record."""
    record = db.query(CastingIn).filter(CastingIn.id == casting_in_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CastingIn not found")
    db.delete(record)
    db.commit()
    logger.info(f"Deleted casting_in id={casting_in_id}")


@router.get("/foundry/{foundry_id}", response_model=list)
def get_casting_ins_by_foundry(foundry_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all inbound records for a specific foundry."""
    records = db.query(CastingIn).filter(CastingIn.foundry_id == foundry_id).offset(skip).limit(limit).all()
    return records


@router.get("/delivery-note/{delivery_note_no}", response_model=CastingInResponse)
def get_casting_in_by_delivery_note(delivery_note_no: str, db: Session = Depends(get_db)):
    """Get casting inbound record by delivery note number."""
    record = db.query(CastingIn).filter(CastingIn.delivery_note_no == delivery_note_no).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return record
