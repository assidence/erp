"""
API Routers Package
"""
from backend.routers.customers import router as customers_router
from backend.routers.foundries import router as foundries_router
from backend.routers.castings import router as castings_router
from backend.routers.casting_ins import router as casting_ins_router
from backend.routers.workpiece_outs import router as workpiece_outs_router
from backend.routers.production_plans import router as production_plans_router
from backend.routers.payment_plans import router as payment_plans_router
from backend.routers.quality_issues import router as quality_issues_router
from backend.routers.attachments import router as attachments_router
from backend.routers.quality_checks import router as quality_checks_router
from backend.routers.production_operations import router as production_operations_router
from backend.routers.process_routes import router as process_routes_router
from backend.routers.technologies import router as technologies_router
from backend.routers.casting_drawings import router as casting_drawings_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.todos import router as todos_router

__all__ = [
    "customers_router",
    "foundries_router",
    "castings_router",
    "casting_ins_router",
    "workpiece_outs_router",
    "production_plans_router",
    "payment_plans_router",
    "quality_issues_router",
    "attachments_router",
    "quality_checks_router",
    "production_operations_router",
    "process_routes_router",
    "technologies_router",
    "casting_drawings_router",
    "dashboard_router",
    "todos_router",
]
