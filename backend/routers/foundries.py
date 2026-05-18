"""
Foundries API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.all_models import Foundry, Customer, CustomerFoundry
from backend.schemas.foundry import (
    FoundryCreate, FoundryUpdate, FoundryResponse,
    FoundryDetailResponse, CustomerSummary
)
from backend.schemas.common import PaginatedResponse
from backend.repositories.foundry import FoundryRepository
from backend.repositories.customer_foundry import CustomerFoundryRepository
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/foundries", tags=["foundries"])


@router.get("/", )
def list_foundries(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all foundries with pagination and optional search."""
    skip = (page - 1) * page_size
    query = db.query(Foundry)

    if search:
        query = query.filter(Foundry.name.contains(search))

    total = query.count()
    items = query.offset(skip).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{foundry_id}", response_model=FoundryDetailResponse)
def get_foundry(foundry_id: int, db: Session = Depends(get_db)):
    """Get a foundry by ID with linked customers."""
    foundry = db.query(Foundry).filter(Foundry.id == foundry_id).first()
    if not foundry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foundry not found")

    # Get linked customers via customer_foundries junction
    linked_customer_rows = (
        db.query(Customer)
        .join(CustomerFoundry, CustomerFoundry.customer_id == Customer.id)
        .filter(CustomerFoundry.foundry_id == foundry_id)
        .all()
    )
    linked_customers = [
        CustomerSummary(
            id=c.id,
            name=c.name,
            contact_person=c.contact_person,
            phone=c.phone,
        )
        for c in linked_customer_rows
    ]

    return FoundryDetailResponse(
        id=foundry.id,
        name=foundry.name,
        contact_person=foundry.contact_person,
        phone=foundry.phone,
        address=foundry.address,
        images=foundry.images or [],
        created_at=foundry.created_at,
        updated_at=foundry.updated_at,
        linked_customers=linked_customers,
    )


@router.post("/", response_model=FoundryResponse, status_code=status.HTTP_201_CREATED)
def create_foundry(data: FoundryCreate, db: Session = Depends(get_db)):
    """Create a new foundry."""
    foundry = Foundry(**data.model_dump())
    db.add(foundry)
    db.commit()
    db.refresh(foundry)
    logger.info(f"Created foundry id={foundry.id}")
    return foundry


@router.put("/{foundry_id}", response_model=FoundryResponse)
def update_foundry(foundry_id: int, data: FoundryUpdate, db: Session = Depends(get_db)):
    """Update a foundry."""
    foundry = db.query(Foundry).filter(Foundry.id == foundry_id).first()
    if not foundry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foundry not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(foundry, key):
            setattr(foundry, key, value)

    db.commit()
    db.refresh(foundry)
    logger.info(f"Updated foundry id={foundry_id}")
    return foundry


@router.delete("/{foundry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_foundry(foundry_id: int, db: Session = Depends(get_db)):
    """Delete a foundry."""
    foundry = db.query(Foundry).filter(Foundry.id == foundry_id).first()
    if not foundry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foundry not found")
    db.delete(foundry)
    db.commit()
    logger.info(f"Deleted foundry id={foundry_id}")


@router.get("/customer/{customer_id}", response_model=List[FoundryResponse])
def get_foundries_by_customer(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all foundries linked to a specific customer."""
    repo = CustomerFoundryRepository(db)
    return repo.get_foundries_by_customer(customer_id, skip=skip, limit=limit)


from pydantic import BaseModel

class LinkRequest(BaseModel):
    customer_ids: list[int]

@router.post("/{foundry_id}/link-customer", response_model=dict)
def link_foundry_to_customer(foundry_id: int, data: LinkRequest, db: Session = Depends(get_db)):
    """Link a foundry to one or more customers."""
    from backend.models.all_models import CustomerFoundry
    for cid in data.customer_ids:
        link = CustomerFoundry(customer_id=cid, foundry_id=foundry_id)
        try:
            db.add(link)
            db.commit()
        except Exception:
            db.rollback()
    logger.info(f"Linked foundry {foundry_id} to customers {data.customer_ids}")
    return {"message": "Linked successfully"}


@router.delete("/{foundry_id}/unlink-customer/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_foundry_from_customer(foundry_id: int, customer_id: int, db: Session = Depends(get_db)):
    """Unlink a foundry from a customer."""
    from backend.models.all_models import CustomerFoundry
    link = db.query(CustomerFoundry).filter(
        CustomerFoundry.customer_id == customer_id,
        CustomerFoundry.foundry_id == foundry_id
    ).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    db.delete(link)
    db.commit()
    logger.info(f"Unlinked foundry {foundry_id} from customer {customer_id}")
