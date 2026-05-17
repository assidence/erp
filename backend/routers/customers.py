"""
Customers API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.models.all_models import Customer, Foundry, Casting, CustomerFoundry, CustomerCasting
from backend.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerDetailResponse, FoundrySummary, CastingSummary
)
from backend.schemas.common import PaginatedResponse
from backend.repositories.customer import CustomerRepository
from backend.repositories.customer_foundry import CustomerFoundryRepository
from backend.repositories.customer_casting import CustomerCastingRepository
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/", )
def list_customers(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all customers with pagination and optional search."""
    skip = (page - 1) * page_size
    query = db.query(Customer)

    if search:
        query = query.filter(Customer.name.contains(search))

    total = query.count()
    items = query.offset(skip).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a customer by ID with related data."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Get linked foundries via junction table
    foundry_links = db.query(Foundry).join(
        CustomerFoundry, CustomerFoundry.foundry_id == Foundry.id
    ).filter(CustomerFoundry.customer_id == customer_id).all()

    # Get linked castings via junction table
    casting_links = db.query(Casting).join(
        CustomerCasting, CustomerCasting.casting_id == Casting.id
    ).filter(CustomerCasting.customer_id == customer_id).all()

    return CustomerDetailResponse(
        id=customer.id,
        name=customer.name,
        contact_person=customer.contact_person,
        phone=customer.phone,
        email=customer.email,
        payment_terms=customer.payment_terms,
        payment_days=customer.payment_days,
        address=customer.address,
        is_active=customer.is_active,
        notes=customer.notes,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        linked_foundries=[
            FoundrySummary(id=f.id, name=f.name, contact_person=f.contact_person, phone=f.phone)
            for f in foundry_links
        ],
        linked_castings=[
            CastingSummary(id=c.id, part_number=c.part_number, name=c.name)
            for c in casting_links
        ]
    )


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    logger.info(f"Created customer id={customer.id}")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(customer, key):
            setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    logger.info(f"Updated customer id={customer_id}")
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    db.delete(customer)
    db.commit()
    logger.info(f"Deleted customer id={customer_id}")


@router.get("/search/", response_model=List[CustomerResponse])
def search_customers(keyword: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Search customers by name or contact person."""
    customers = db.query(Customer).filter(
        (Customer.name.contains(keyword)) | (Customer.contact_person.contains(keyword))
    ).offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}/foundries", response_model=List)
def get_customer_foundries(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all foundries linked to a specific customer."""
    repo = CustomerFoundryRepository(db)
    return repo.get_foundries_by_customer(customer_id, skip=skip, limit=limit)


@router.get("/{customer_id}/castings", response_model=List)
def get_customer_castings(customer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all castings linked to a specific customer."""
    repo = CustomerCastingRepository(db)
    return repo.get_castings_by_customer(customer_id, skip=skip, limit=limit)
