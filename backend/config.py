"""
ERP Backend Configuration
Centralized configuration management with environment variable support.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import logging


# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "Mechanical Processing Factory ERP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/erp.db"

    # Upload directory
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    """Configure application logging."""
    import logging

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATE_FORMAT,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module."""
    import logging
    return logging.getLogger(name)