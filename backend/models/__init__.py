"""
ERP Backend Models Package
"""
from backend.database import Base, TimestampMixin
from backend.models.all_models import (
    Customer,
    Foundry,
    Casting,
    PartDrawing,
    CastingIn,
    WorkpieceOut,
    ProductionPlan,
    PaymentPlan,
    QualityIssue,
    Attachment,
    QualityCheck,
    ProductionOperation,
    ProcessRoute,
    Technology,
)

# Backward compatibility aliases
Supplier = Foundry
Part = Casting
MaterialIn = CastingIn
ProductOut = WorkpieceOut

__all__ = [
    "Base",
    "TimestampMixin",
    "Customer",
    "Foundry",
    "Casting",
    "PartDrawing",
    "CastingIn",
    "WorkpieceOut",
    "ProductionPlan",
    "PaymentPlan",
    "QualityIssue",
    "Attachment",
    "QualityCheck",
    "ProductionOperation",
    "ProcessRoute",
    "Technology",
    # Aliases
    "Supplier",
    "Part",
    "MaterialIn",
    "ProductOut",
]
