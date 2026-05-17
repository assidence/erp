"""
PaymentPlans API Router — Receivables management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal

from backend.database import get_db
from backend.models.all_models import PaymentPlan, ProductionPlan, WorkpieceOut, WorkpieceOutItem, Customer
from backend.schemas.payment_plan import PaymentPlanCreate, PaymentPlanUpdate, PaymentPlanResponse
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/payment-plans", tags=["payment-plans"])


@router.get("/", )
def list_payment_plans(
    page: int = 1,
    page_size: int = 100,
    customer_id: int = None,
    status_filter: str = None,
    overdue: bool = None,
    settled: bool = None,
    db: Session = Depends(get_db)
):
    """List payment plans (receivables) with optional filters."""
    skip = (page - 1) * page_size
    query = db.query(PaymentPlan)
    now = datetime.now()

    if customer_id is not None:
        query = query.filter(PaymentPlan.customer_id == customer_id)

    if status_filter:
        query = query.filter(PaymentPlan.status == status_filter)

    # Overdue: any non-paid status with past expected_date
    if overdue is True:
        query = query.filter(
            PaymentPlan.status != "paid",
            PaymentPlan.expected_date < now
        )
    elif overdue is False:
        query = query.filter(
            (PaymentPlan.status == "paid") | (PaymentPlan.expected_date >= now) | (PaymentPlan.expected_date.is_(None))
        )

    if settled is True:
        query = query.filter(PaymentPlan.status.in_(["paid", "partial"]))
    elif settled is False:
        query = query.filter(PaymentPlan.status.notin_(["paid", "partial"]))

    total = query.count()
    items = query.order_by(PaymentPlan.expected_date.asc().nullslast()).offset(skip).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{payment_plan_id}", response_model=PaymentPlanResponse)
def get_payment_plan(payment_plan_id: int, db: Session = Depends(get_db)):
    """Get a payment plan by ID."""
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == payment_plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PaymentPlan not found")
    return plan


@router.post("/", response_model=PaymentPlanResponse, status_code=status.HTTP_201_CREATED)
def create_payment_plan(data: PaymentPlanCreate, db: Session = Depends(get_db)):
    """Create a new payment plan (receivable)."""
    plan = PaymentPlan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    logger.info(f"Created payment_plan id={plan.id}")
    return plan


@router.put("/{payment_plan_id}", response_model=PaymentPlanResponse)
def update_payment_plan(payment_plan_id: int, data: PaymentPlanUpdate, db: Session = Depends(get_db)):
    """Update a payment plan (receivable)."""
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == payment_plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PaymentPlan not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(plan, key):
            setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    logger.info(f"Updated payment_plan id={payment_plan_id}")
    return plan


@router.delete("/{payment_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_plan(payment_plan_id: int, db: Session = Depends(get_db)):
    """Delete a payment plan."""
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == payment_plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PaymentPlan not found")
    db.delete(plan)
    db.commit()
    logger.info(f"Deleted payment_plan id={payment_plan_id}")


@router.get("/unaligned-plans/")
def get_unaligned_production_plans(db: Session = Depends(get_db)):
    """
    Return production plans that have no PaymentPlan aligned, with reasons why.
    A plan is 'aligned' when at least one of its completed WorkpieceOuts generated a PaymentPlan.
    """
    # Get all production plans with their workpiece outs
    plans = db.query(ProductionPlan).order_by(ProductionPlan.due_date.asc()).all()

    # Get customer names cache
    customers_cache = {c.id: c.name for c in db.query(Customer).all()}

    # Get all workpiece_out_ids that have payment plans
    paid_wo_ids = {pp.workpiece_out_id for pp in db.query(PaymentPlan).all()}

    # Get all workpiece outs with their plans
    all_wos = db.query(WorkpieceOut).all()
    wo_by_plan = {}
    for wo in all_wos:
        wo_by_plan.setdefault(wo.production_plan_id, []).append(wo)

    result = []
    for plan in plans:
        wos = wo_by_plan.get(plan.id, [])

        # Check alignment
        completed_wos = [wo for wo in wos if wo.status == 'completed']
        aligned_wos = [wo for wo in completed_wos if wo.id in paid_wo_ids]

        if len(aligned_wos) == len(completed_wos) and len(completed_wos) > 0:
            continue

        # Determine reason
        if len(wos) == 0:
            reason = "尚未生成出库记录"
        elif len(completed_wos) == 0:
            pending = [wo for wo in wos if wo.status == 'pending']
            shipped = [wo for wo in wos if wo.status == 'shipped']
            if pending and not shipped:
                reason = f"出库单尚未发货（{len(pending)}张待发货）"
            elif shipped:
                reason = f"出库单尚未完成（{len(shipped)}张已发货未完成）"
            else:
                reason = f"出库单状态均为{','.join(set(wo.status for wo in wos))}"
        else:
            reason = f"{len(completed_wos) - len(aligned_wos)}张出库单已完成但未生成收款计划"

        # Calculate total shipped
        total_shipped = Decimal("0")
        for wo in wos:
            items = db.query(WorkpieceOutItem).filter(
                WorkpieceOutItem.workpiece_out_id == wo.id
            ).all()
            for it in items:
                total_shipped += Decimal(str(it.quantity))

        result.append({
            "id": plan.id,
            "plan_no": plan.plan_no,
            "customer_id": plan.customer_id,
            "customer_name": customers_cache.get(plan.customer_id),
            "due_date": plan.due_date.isoformat() if plan.due_date else None,
            "status": plan.status,
            "wo_count": len(wos),
            "completed_wo_count": len(completed_wos),
            "total_shipped": float(total_shipped),
            "reason": reason,
        })

    return result
