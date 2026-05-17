"""
Pydantic Schemas Package
Request/Response schemas for API validation.
"""
from backend.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from backend.schemas.foundry import FoundryCreate, FoundryUpdate, FoundryResponse
from backend.schemas.casting import CastingCreate, CastingUpdate, CastingResponse, CastingDrawingCreate, CastingDrawingUpdate, CastingDrawingResponse
from backend.schemas.casting_in import CastingInCreate, CastingInUpdate, CastingInResponse
from backend.schemas.workpiece_out import WorkpieceOutCreate, WorkpieceOutUpdate, WorkpieceOutResponse
from backend.schemas.production_plan import ProductionPlanCreate, ProductionPlanUpdate, ProductionPlanResponse
from backend.schemas.payment_plan import PaymentPlanCreate, PaymentPlanUpdate, PaymentPlanResponse
from backend.schemas.quality_issue import QualityIssueCreate, QualityIssueUpdate, QualityIssueResponse
from backend.schemas.attachment import AttachmentCreate, AttachmentUpdate, AttachmentResponse

__all__ = [
    "CustomerCreate", "CustomerUpdate", "CustomerResponse",
    "FoundryCreate", "FoundryUpdate", "FoundryResponse",
    "CastingCreate", "CastingUpdate", "CastingResponse",
    "CastingDrawingCreate", "CastingDrawingUpdate", "CastingDrawingResponse",
    "CastingInCreate", "CastingInUpdate", "CastingInResponse",
    "WorkpieceOutCreate", "WorkpieceOutUpdate", "WorkpieceOutResponse",
    "ProductionPlanCreate", "ProductionPlanUpdate", "ProductionPlanResponse",
    "PaymentPlanCreate", "PaymentPlanUpdate", "PaymentPlanResponse",
    "QualityIssueCreate", "QualityIssueUpdate", "QualityIssueResponse",
    "AttachmentCreate", "AttachmentUpdate", "AttachmentResponse",
]