"""
ProductionPlans API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from decimal import Decimal

from backend.database import get_db
from backend.models.all_models import ProductionPlan, ProductionPlanItem
from backend.schemas.production_plan import (
    ProductionPlanCreate, ProductionPlanUpdate, ProductionPlanResponse,
    ProductionPlanItemResponse
)
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/production-plans", tags=["production-plans"])


def _get_plan_with_items(plan: ProductionPlan, db: Session) -> dict:
    """Serialize a ProductionPlan with its items and remaining quantities."""
    from backend.models.all_models import WorkpieceOutItem
    items_raw = db.query(ProductionPlanItem).filter(ProductionPlanItem.plan_id == plan.id).all()

    # Calculate remaining quantity per item
    shipped_qty = {}
    shipped_rows = db.query(WorkpieceOutItem).filter(
        WorkpieceOutItem.production_plan_item_id.in_([it.id for it in items_raw])
    ).all()
    for row in shipped_rows:
        shipped_qty[row.production_plan_item_id] = (
            shipped_qty.get(row.production_plan_item_id, Decimal("0")) + row.quantity
        )

    items = []
    for it in items_raw:
        shipped = shipped_qty.get(it.id, Decimal("0"))
        remaining = it.required_quantity - shipped
        item_resp = ProductionPlanItemResponse.model_validate(it).model_dump()
        item_resp["remaining_quantity"] = max(remaining, Decimal("0"))
        items.append(item_resp)

    resp = ProductionPlanResponse.model_validate(plan).model_dump()
    resp["items"] = items
    return resp


@router.get("/", )
def list_production_plans(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all production plans with pagination."""
    skip = (page - 1) * page_size
    query = db.query(ProductionPlan)

    if search:
        query = query.filter(ProductionPlan.plan_no.contains(search))

    total = query.count()
    plans = query.order_by(ProductionPlan.due_date.asc()).offset(skip).limit(page_size).all()
    items = [_get_plan_with_items(p, db) for p in plans]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{plan_id}")
def get_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a production plan by ID with items."""
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProductionPlan not found")
    return _get_plan_with_items(plan, db)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_production_plan(data: ProductionPlanCreate, db: Session = Depends(get_db)):
    """Create a new production plan with items."""
    from datetime import datetime as dt

    # Auto-generate plan_no if not provided
    plan_no = data.plan_no and data.plan_no.strip()
    if not plan_no:
        year = dt.now().year
        # Find highest existing plan_no for current year
        existing = db.query(ProductionPlan).filter(
            ProductionPlan.plan_no.like(f"PP-{year}-%")
        ).order_by(ProductionPlan.id.desc()).first()
        if existing:
            try:
                seq = int(existing.plan_no.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        plan_no = f"PP-{year}-{seq:04d}"

    # Create plan header
    plan = ProductionPlan(
        plan_no=plan_no,
        customer_id=data.customer_id,
        start_date=data.start_date,
        due_date=data.due_date,
        status=data.status or "pending",
        notes=data.notes,
        images=data.images or []
    )
    db.add(plan)
    db.flush()  # Get plan.id

    # Create plan items
    for item_data in data.items:
        item = ProductionPlanItem(
            plan_id=plan.id,
            casting_id=item_data.casting_id,
            required_quantity=item_data.required_quantity,
            produced_quantity=item_data.produced_quantity or 0,
            unit_price=item_data.unit_price,
            remaining_quantity=item_data.required_quantity  # nothing shipped yet
        )
        db.add(item)

    db.commit()
    db.refresh(plan)
    logger.info(f"Created production_plan id={plan.id} plan_no={plan_no} with {len(data.items)} items")
    return _get_plan_with_items(plan, db)


@router.put("/{plan_id}")
def update_production_plan(plan_id: int, data: ProductionPlanUpdate, db: Session = Depends(get_db)):
    """Update a production plan (header + items)."""
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProductionPlan not found")

    # Update header fields
    update_data = data.model_dump(exclude_unset=True, exclude={"items"})
    for key, value in update_data.items():
        if hasattr(plan, key):
            setattr(plan, key, value)

    # Update items if provided
    if data.items is not None:
        # Delete old items
        db.query(ProductionPlanItem).filter(ProductionPlanItem.plan_id == plan_id).delete()
        # Create new items
        for item_data in data.items:
            item = ProductionPlanItem(
                plan_id=plan.id,
                casting_id=item_data.casting_id,
                required_quantity=item_data.required_quantity,
                produced_quantity=item_data.produced_quantity or 0,
                unit_price=item_data.unit_price,
                remaining_quantity=item_data.required_quantity
            )
            db.add(item)

    db.commit()
    db.refresh(plan)
    logger.info(f"Updated production_plan id={plan_id}")
    return _get_plan_with_items(plan, db)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_production_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a production plan and its items."""
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProductionPlan not found")

    # Cascade delete items
    db.query(ProductionPlanItem).filter(ProductionPlanItem.plan_id == plan_id).delete()
    db.delete(plan)
    db.commit()
    logger.info(f"Deleted production_plan id={plan_id}")
