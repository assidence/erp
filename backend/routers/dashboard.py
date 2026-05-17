"""
Dashboard API Router
Provides statistics and recent activity for the dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.all_models import (
    Customer, Foundry, CastingIn, WorkpieceOut, WorkpieceOutItem,
    PaymentPlan, ProductionPlan, ProductionPlanItem, QualityIssue, Casting
)
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics.
    Returns counts and sums for dashboard cards.
    """
    total_customers = db.query(Customer).count()
    total_foundries = db.query(Foundry).count()

    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_outs = db.query(WorkpieceOut).filter(
        WorkpieceOut.created_at >= start_of_month
    ).count()

    pending_payments = db.query(func.coalesce(func.sum(PaymentPlan.amount), 0)).filter(
        PaymentPlan.status == "pending"
    ).scalar() or 0

    return {
        "totalCustomers": total_customers,
        "totalSuppliers": total_foundries,
        "monthlyOrders": monthly_outs,
        "pendingPayments": float(pending_payments) if pending_payments else 0
    }


@router.get("/recent")
def get_recent_activity(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get recent activity for the dashboard.
    Combines recent casting ins, workpiece outs, production plans, and payments.
    """
    activities = []
    activity_id = 0

    # Recent casting ins
    recent_ins = db.query(CastingIn).order_by(desc(CastingIn.created_at)).limit(limit).all()
    for ins in recent_ins:
        activity_id += 1
        foundry = db.query(Foundry).filter(Foundry.id == ins.foundry_id).first()
        casting = db.query(Casting).filter(Casting.id == ins.casting_id).first()
        activities.append({
            "id": activity_id,
            "type": "material_in",
            "description": f"铸件入库 - {foundry.name if foundry else '未知'} {casting.part_number if casting else ''} {ins.quantity}件",
            "time": ins.created_at.strftime("%H:%M") if ins.created_at else "未知",
            "_sort": ins.created_at,
        })

    # Recent workpiece outs (header + items model)
    recent_outs = db.query(WorkpieceOut).order_by(desc(WorkpieceOut.created_at)).limit(limit).all()
    for out in recent_outs:
        activity_id += 1
        customer = db.query(Customer).filter(Customer.id == out.customer_id).first()
        item_count = db.query(WorkpieceOutItem).filter(WorkpieceOutItem.workpiece_out_id == out.id).count()
        activities.append({
            "id": activity_id,
            "type": "product_out",
            "description": f"工件出库 - {customer.name if customer else '未知'} {item_count}种零件 {out.delivery_note_no}",
            "time": out.created_at.strftime("%H:%M") if out.created_at else "未知",
            "_sort": out.created_at,
        })

    # Recent production plans
    recent_plans = db.query(ProductionPlan).order_by(desc(ProductionPlan.created_at)).limit(limit).all()
    for plan in recent_plans:
        activity_id += 1
        item_count = db.query(ProductionPlanItem).filter(ProductionPlanItem.plan_id == plan.id).count()
        activities.append({
            "id": activity_id,
            "type": "production",
            "description": f"生产计划 - {plan.plan_no} {item_count}种零件",
            "time": plan.created_at.strftime("%H:%M") if plan.created_at else "未知",
            "_sort": plan.created_at,
        })

    # Recent payment plans
    recent_payments = db.query(PaymentPlan).order_by(desc(PaymentPlan.created_at)).limit(limit).all()
    for payment in recent_payments:
        activity_id += 1
        customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
        activities.append({
            "id": activity_id,
            "type": "payment",
            "description": f"付款计划 - {customer.name if customer else '未知'} {float(payment.amount)}元",
            "time": payment.created_at.strftime("%H:%M") if payment.created_at else "未知",
            "_sort": payment.created_at,
        })

    # Sort by created_at descending
    activities.sort(key=lambda x: x.get("_sort") or datetime.min, reverse=True)
    for a in activities:
        a.pop("_sort", None)
    return activities[:limit]


@router.get("/recent-product-outs")
def get_recent_product_outs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get recent product outbound records."""
    recent_outs = db.query(WorkpieceOut).order_by(desc(WorkpieceOut.created_at)).offset(skip).limit(limit).all()
    result = []
    for out in recent_outs:
        items = db.query(WorkpieceOutItem).filter(WorkpieceOutItem.workpiece_out_id == out.id).all()
        total_qty = sum(float(it.quantity) for it in items)
        result.append({
            "id": out.id,
            "delivery_note_no": out.delivery_note_no,
            "total_quantity": total_qty,
            "item_count": len(items),
            "delivery_date": out.delivery_date.isoformat() if out.delivery_date else None,
            "status": out.status,
            "created_at": out.created_at.isoformat() if out.created_at else None,
        })
    return result


@router.get("/overdue-payments")
def get_overdue_payments(db: Session = Depends(get_db)):
    """Get overdue payment plans."""
    now = datetime.now()
    overdue_payments = db.query(PaymentPlan).filter(
        PaymentPlan.status == "pending",
        PaymentPlan.expected_date < now
    ).all()
    result = []
    for payment in overdue_payments:
        customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
        result.append({
            "id": payment.id,
            "customer_name": customer.name if customer else "未知",
            "amount": float(payment.amount),
            "expected_date": payment.expected_date.isoformat() if payment.expected_date else None,
            "overdue_days": (now - payment.expected_date).days if payment.expected_date else 0
        })
    return result


@router.get("/quality-stats")
def get_quality_stats(db: Session = Depends(get_db)):
    """Get quality issue statistics."""
    total_issues = db.query(QualityIssue).count()
    open_issues = db.query(QualityIssue).filter(QualityIssue.status == "open").count()
    resolved_issues = db.query(QualityIssue).filter(QualityIssue.status == "resolved").count()
    return {
        "total": total_issues,
        "open": open_issues,
        "resolved": resolved_issues,
        "resolution_rate": round(resolved_issues / total_issues * 100, 1) if total_issues > 0 else 0
    }
