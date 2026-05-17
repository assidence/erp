"""
WorkpieceOuts API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.all_models import WorkpieceOut, WorkpieceOutItem, PaymentPlan
from backend.schemas.workpiece_out import (
    WorkpieceOutCreate, WorkpieceOutUpdate, WorkpieceOutResponse,
    WorkpieceOutItemResponse
)
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/workpiece-outs", tags=["workpiece-outs"])


def _get_out_with_items(out: WorkpieceOut, db: Session) -> dict:
    """Serialize a WorkpieceOut with its items."""
    items = db.query(WorkpieceOutItem).filter(WorkpieceOutItem.workpiece_out_id == out.id).all()
    resp = WorkpieceOutResponse.model_validate(out).model_dump()
    resp["items"] = [
        WorkpieceOutItemResponse.model_validate(it).model_dump() for it in items
    ]
    return resp


@router.get("/", )
def list_workpiece_outs(
    page: int = 1,
    page_size: int = 100,
    search: str = "",
    db: Session = Depends(get_db)
):
    """List all workpiece outbound records with pagination."""
    skip = (page - 1) * page_size
    query = db.query(WorkpieceOut)

    if search:
        query = query.filter(WorkpieceOut.delivery_note_no.contains(search))

    total = query.count()
    records = query.order_by(WorkpieceOut.created_at.desc()).offset(skip).limit(page_size).all()
    items = [_get_out_with_items(r, db) for r in records]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{out_id}")
def get_workpiece_out(out_id: int, db: Session = Depends(get_db)):
    """Get a workpiece outbound record by ID with items."""
    record = db.query(WorkpieceOut).filter(WorkpieceOut.id == out_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WorkpieceOut not found")
    return _get_out_with_items(record, db)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_workpiece_out(data: WorkpieceOutCreate, db: Session = Depends(get_db)):
    """Create a new workpiece outbound record with items."""
    existing = db.query(WorkpieceOut).filter(
        WorkpieceOut.delivery_note_no == data.delivery_note_no
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Delivery note '{data.delivery_note_no}' already exists"
        )

    # Create header
    out = WorkpieceOut(
        delivery_note_no=data.delivery_note_no,
        production_plan_id=data.production_plan_id,
        customer_id=data.customer_id,
        delivery_date=data.delivery_date,
        shipping_address=data.shipping_address,
        status=data.status or "pending",
        notes=data.notes,
        images=data.images or []
    )
    db.add(out)
    db.flush()  # Get out.id

    # Create items
    for item_data in data.items:
        item = WorkpieceOutItem(
            workpiece_out_id=out.id,
            production_plan_item_id=item_data.production_plan_item_id,
            casting_id=item_data.casting_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price
        )
        db.add(item)

    db.commit()
    db.refresh(out)
    logger.info(f"Created workpiece_out id={out.id} with {len(data.items)} items")
    return _get_out_with_items(out, db)


@router.put("/{out_id}")
def update_workpiece_out(out_id: int, data: WorkpieceOutUpdate, db: Session = Depends(get_db)):
    """Update a workpiece outbound record (header + items)."""
    out = db.query(WorkpieceOut).filter(WorkpieceOut.id == out_id).first()
    if not out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WorkpieceOut not found")

    # Track if status is being changed to completed
    new_status = data.status
    old_status = out.status
    auto_generate_payment = (
        new_status == "completed" and old_status != "completed"
    )

    # Update header
    update_data = data.model_dump(exclude_unset=True, exclude={"items"})
    for key, value in update_data.items():
        if hasattr(out, key):
            setattr(out, key, value)

    # Update items if provided
    if data.items is not None:
        db.query(WorkpieceOutItem).filter(
            WorkpieceOutItem.workpiece_out_id == out_id
        ).delete()
        for item_data in data.items:
            item = WorkpieceOutItem(
                workpiece_out_id=out.id,
                production_plan_item_id=item_data.production_plan_item_id,
                casting_id=item_data.casting_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price
            )
            db.add(item)

    # Auto-generate PaymentPlan when status changes to completed
    if auto_generate_payment:
        # Check if payment plan already exists for this shipment
        existing_pp = db.query(PaymentPlan).filter(
            PaymentPlan.workpiece_out_id == out.id
        ).first()
        if not existing_pp:
            # Calculate total amount from all items
            items = db.query(WorkpieceOutItem).filter(
                WorkpieceOutItem.workpiece_out_id == out.id
            ).all()
            total = sum(
                float(it.quantity) * float(it.unit_price or 0)
                for it in items
            )
            if total > 0:
                pp = PaymentPlan(
                    customer_id=out.customer_id,
                    workpiece_out_id=out.id,
                    expected_date=None,
                    amount=total,
                    status="pending",
                )
                db.add(pp)
                logger.info(f"Auto-created PaymentPlan for workpiece_out id={out.id}, amount={total}")

    db.commit()
    db.refresh(out)
    logger.info(f"Updated workpiece_out id={out_id}")
    return _get_out_with_items(out, db)


@router.delete("/{out_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workpiece_out(out_id: int, db: Session = Depends(get_db)):
    """Delete a workpiece outbound record and its items."""
    out = db.query(WorkpieceOut).filter(WorkpieceOut.id == out_id).first()
    if not out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WorkpieceOut not found")

    db.query(WorkpieceOutItem).filter(
        WorkpieceOutItem.workpiece_out_id == out_id
    ).delete()
    db.delete(out)
    db.commit()
    logger.info(f"Deleted workpiece_out id={out_id}")
