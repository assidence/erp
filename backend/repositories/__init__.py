"""
Repository Layer Package
Data access layer with high cohesion and low coupling.
Each entity has its own repository.
"""
from backend.repositories.customer import CustomerRepository
from backend.repositories.foundry import FoundryRepository
from backend.repositories.casting import CastingRepository, CastingDrawingRepository
from backend.repositories.casting_in import CastingInRepository
from backend.repositories.workpiece_out import WorkpieceOutRepository
from backend.repositories.production_plan import ProductionPlanRepository
from backend.repositories.payment_plan import PaymentPlanRepository
from backend.repositories.quality_issue import QualityIssueRepository
from backend.repositories.attachment import AttachmentRepository

__all__ = [
    "CustomerRepository",
    "FoundryRepository",
    "CastingRepository",
    "CastingDrawingRepository",
    "CastingInRepository",
    "WorkpieceOutRepository",
    "ProductionPlanRepository",
    "PaymentPlanRepository",
    "QualityIssueRepository",
    "AttachmentRepository",
]