"""
FastAPI Application Entry Point
Mechanical Processing Factory ERP System Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings, setup_logging, get_logger
from backend.database import init_db
from backend.routers import (
    customers_router,
    foundries_router,
    castings_router,
    casting_ins_router,
    workpiece_outs_router,
    production_plans_router,
    payment_plans_router,
    quality_issues_router,
    attachments_router,
    quality_checks_router,
    production_operations_router,
    process_routes_router,
    technologies_router,
    casting_drawings_router,
    dashboard_router,
    todos_router,
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Mechanical Processing Factory ERP System",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("Database initialized successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down ERP application")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Version endpoint
@app.get("/api/version")
async def get_version():
    """Get build/deployment version stamp."""
    return {
        "version": "1.0.0",
        "build_time": "2026-05-17",
        "git_commit": "dev",
    }


# Include all routers
app.include_router(customers_router)
app.include_router(foundries_router)
app.include_router(castings_router)
app.include_router(casting_ins_router)
app.include_router(workpiece_outs_router)
app.include_router(production_plans_router)
app.include_router(payment_plans_router)
app.include_router(quality_issues_router)
app.include_router(attachments_router)
app.include_router(quality_checks_router)
app.include_router(production_operations_router)
app.include_router(process_routes_router)
app.include_router(technologies_router)
app.include_router(casting_drawings_router)
app.include_router(dashboard_router)
app.include_router(todos_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)