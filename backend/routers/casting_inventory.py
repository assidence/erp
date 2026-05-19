"""
Casting Inventory API Router
Tracks current stock, allocated quantities, and transaction history per casting.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime

from backend.database import get_db
from backend.models.all_models import (
    Casting, CastingIn, WorkpieceOutItem,
    ProductionPlan, ProductionPlanItem, WorkpieceOut
)
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/casting-inventory", tags=["casting-inventory"])


@router.get("/")
def list_casting_inventory(db: Session = Depends(get_db)):
    """
    List all castings with their current inventory status:
    - incoming: total from approved casting_ins
    - shipped: total from workpiece_outs (shipped/completed only)
    - allocated: total required by active production plans
    - available: incoming - shipped - allocated
    """
    # Get all castings
    castings = db.query(Casting).all()
    casting_ids = [c.id for c in castings]

    # Compute incoming quantities per casting (from approved casting_ins)
    incoming_q = {}
    if casting_ids:
        rows = db.query(
            CastingIn.casting_id,
            func.coalesce(func.sum(CastingIn.quantity), 0).label("total")
        ).filter(
            CastingIn.casting_id.in_(casting_ids),
            CastingIn.status != "rejected"
        ).group_by(CastingIn.casting_id).all()
        incoming_q = {r.casting_id: Decimal(str(r.total)) for r in rows}

    # Compute shipped quantities per casting (from completed workpiece_outs)
    shipped_q = {}
    if casting_ids:
        rows = db.query(
            WorkpieceOutItem.casting_id,
            func.coalesce(func.sum(WorkpieceOutItem.quantity), 0).label("total")
        ).join(
            WorkpieceOut, WorkpieceOutItem.workpiece_out_id == WorkpieceOut.id
        ).filter(
            WorkpieceOutItem.casting_id.in_(casting_ids),
            WorkpieceOut.status == "completed"
        ).group_by(WorkpieceOutItem.casting_id).all()
        shipped_q = {r.casting_id: Decimal(str(r.total)) for r in rows}

    # Compute allocated quantities (from active production plans, not completed/delayed)
    allocated_q = {}
    if casting_ids:
        active_plan_ids = [
            r[0] for r in db.query(ProductionPlan.id).filter(
                ProductionPlan.status.in_(["pending", "in_progress"])
            ).all()
        ]
        if active_plan_ids:
            rows = db.query(
                ProductionPlanItem.casting_id,
                func.coalesce(func.sum(ProductionPlanItem.required_quantity), 0).label("total")
            ).filter(
                ProductionPlanItem.casting_id.in_(casting_ids),
                ProductionPlanItem.plan_id.in_(active_plan_ids)
            ).group_by(ProductionPlanItem.casting_id).all()
            allocated_q = {r.casting_id: Decimal(str(r.total)) for r in rows}

    result = []
    for c in castings:
        incoming = incoming_q.get(c.id, Decimal("0"))
        shipped = shipped_q.get(c.id, Decimal("0"))
        allocated = allocated_q.get(c.id, Decimal("0"))
        available = incoming - shipped - allocated
        result.append({
            "casting_id": c.id,
            "casting_name": c.name,
            "casting_part_number": c.part_number,
            "customer_id": c.customer_id,
            "latest_price": c.latest_price,
            "incoming": float(incoming),
            "shipped": float(shipped),
            "allocated": float(allocated),
            "available": float(available) if available >= 0 else 0.0,
            "available_raw": str(available),
        })

    return {"items": result, "total": len(result)}


@router.get("/casting/{casting_id}/transactions")
def get_casting_transactions(casting_id: int, db: Session = Depends(get_db)):
    """
    Get transaction history for a specific casting.
    Returns all incoming (casting_ins) and outgoing (workpiece_out_items) records.
    """
    # Get casting info
    casting = db.query(Casting).filter(Casting.id == casting_id).first()
    if not casting:
        return {"casting": None, "transactions": []}

    transactions = []

    # Incoming records (casting_ins)
    ins = db.query(CastingIn).filter(
        CastingIn.casting_id == casting_id
    ).order_by(CastingIn.incoming_date.desc()).all()

    for ci in ins:
        transactions.append({
            "id": ci.id,
            "type": "incoming",
            "source": "入库",
            "ref_no": ci.delivery_note_no,
            "quantity": float(ci.quantity),
            "date": ci.incoming_date.isoformat() if ci.incoming_date else None,
            "status": ci.status,
            "notes": ci.notes,
        })

    # Outgoing records (workpiece_out_items) - joined with workpiece_out for context
    from backend.models.all_models import WorkpieceOut
    outs = db.query(WorkpieceOutItem, WorkpieceOut).join(
        WorkpieceOut, WorkpieceOutItem.workpiece_out_id == WorkpieceOut.id
    ).filter(
        WorkpieceOutItem.casting_id == casting_id
    ).order_by(WorkpieceOut.delivery_date.desc()).all()

    for oi, wo in outs:
        transactions.append({
            "id": oi.id,
            "type": "outgoing",
            "source": "出库",
            "ref_no": wo.delivery_note_no,
            "quantity": -float(oi.quantity),  # negative to indicate outflow
            "date": wo.delivery_date.isoformat() if wo.delivery_date else None,
            "status": wo.status,
            "notes": wo.notes,
        })

    # Sort by date descending
    transactions.sort(key=lambda x: x["date"] or "", reverse=True)

    return {
        "casting": {
            "id": casting.id,
            "name": casting.name,
            "part_number": casting.part_number,
            "customer_id": casting.customer_id,
        },
        "transactions": transactions,
    }


@router.get("/available")
def get_available_for_castings(
    casting_ids: str,  # comma-separated list of casting IDs
    db: Session = Depends(get_db)
):
    """
    Get available quantities for a list of castings.
    Used by ProductionPlan form to show stock when selecting parts.
    Query param: casting_ids=1,2,3
    """
    ids = [int(x.strip()) for x in casting_ids.split(",") if x.strip()]

    if not ids:
        return {"items": []}

    # Incoming
    incoming_q = {}
    rows = db.query(
        CastingIn.casting_id,
        func.coalesce(func.sum(CastingIn.quantity), 0).label("total")
    ).filter(
        CastingIn.casting_id.in_(ids),
        CastingIn.status != "rejected"
    ).group_by(CastingIn.casting_id).all()
    incoming_q = {r.casting_id: Decimal(str(r.total)) for r in rows}

    # Shipped (only from completed workpiece_outs)
    from backend.models.all_models import WorkpieceOut
    shipped_q = {}
    rows = db.query(
        WorkpieceOutItem.casting_id,
        func.coalesce(func.sum(WorkpieceOutItem.quantity), 0).label("total")
    ).join(
        WorkpieceOut, WorkpieceOutItem.workpiece_out_id == WorkpieceOut.id
    ).filter(
        WorkpieceOutItem.casting_id.in_(ids),
        WorkpieceOut.status == "completed"
    ).group_by(WorkpieceOutItem.casting_id).all()
    shipped_q = {r.casting_id: Decimal(str(r.total)) for r in rows}

    # Allocated (active plans)
    active_plan_ids = [
        r[0] for r in db.query(ProductionPlan.id).filter(
            ProductionPlan.status.in_(["pending", "in_progress"])
        ).all()
    ]
    allocated_q = {}
    if active_plan_ids:
        rows = db.query(
            ProductionPlanItem.casting_id,
            func.coalesce(func.sum(ProductionPlanItem.required_quantity), 0).label("total")
        ).filter(
            ProductionPlanItem.casting_id.in_(ids),
            ProductionPlanItem.plan_id.in_(active_plan_ids)
        ).group_by(ProductionPlanItem.casting_id).all()
        allocated_q = {r.casting_id: Decimal(str(r.total)) for r in rows}

    result = []
    for cid in ids:
        incoming = incoming_q.get(cid, Decimal("0"))
        shipped = shipped_q.get(cid, Decimal("0"))
        allocated = allocated_q.get(cid, Decimal("0"))
        available = incoming - shipped - allocated
        result.append({
            "casting_id": cid,
            "incoming": float(incoming),
            "shipped": float(shipped),
            "allocated": float(allocated),
            "available": float(available) if available >= 0 else 0.0,
        })

    return {"items": result}
