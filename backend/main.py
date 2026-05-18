"""
FastAPI Application Entry Point
Mechanical Processing Factory ERP System Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings, setup_logging, get_logger
from backend.database import init_db
from backend.routers import (
    customers_router, foundries_router, castings_router, casting_ins_router,
    workpiece_outs_router, production_plans_router, payment_plans_router,
    quality_issues_router, attachments_router, quality_checks_router,
    production_operations_router, process_routes_router, technologies_router,
    casting_drawings_router, dashboard_router, todos_router,
)

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Mechanical Processing Factory ERP System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("Database initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down ERP application")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/api/version")
async def get_version():
    return {"version": "1.0.0", "build_time": "2026-05-17", "git_commit": "dev"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("/home/ubuntu/erp/backend/favicon.ico", media_type="image/x-icon")

# Mount upload directory for serving static files
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

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
