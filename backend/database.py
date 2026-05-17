"""
SQLAlchemy Database Connection and Session Management
"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base, declarative_mixin
from sqlalchemy import Column, DateTime
from datetime import datetime
from typing import Generator

from backend.config import settings, get_logger

logger = get_logger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-specific for FastAPI
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base with default timestamp mixin
Base = declarative_base()


@declarative_mixin
class TimestampMixin:
    """
    Mixin to add created_at and updated_at auto fields.
    Uses Python-side default to avoid SQLite RETURNING clause issues.
    """

    created_at = Column(
        DateTime,
        default=datetime.utcnow,  # Python-side default (no server_default)
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,  # Python-side default
        onupdate=datetime.utcnow,  # Auto-update on modification
        nullable=False
    )


def get_db() -> Generator:
    """
    Get database session.
    Yields a session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    from backend.models import (
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
    )

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


def drop_db() -> None:
    """
    Drop all database tables (use with caution).
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped.")