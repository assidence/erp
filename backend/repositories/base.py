"""
Base Repository
Generic CRUD operations for all entities.
"""
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from backend.database import Base
from backend.config import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        """Get entity by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, entity: ModelType) -> ModelType:
        """Create a new entity."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        logger.info(f"Created {self.model.__tablename__} with id={entity.id}")
        return entity

    def update(self, id: int, data: dict) -> Optional[ModelType]:
        """Update an entity by ID."""
        entity = self.get(id)
        if entity:
            for key, value in data.items():
                if hasattr(entity, key) and value is not None:
                    setattr(entity, key, value)
            self.db.commit()
            self.db.refresh(entity)
            logger.info(f"Updated {self.model.__tablename__} with id={id}")
        return entity

    def delete(self, id: int) -> bool:
        """Delete an entity by ID."""
        entity = self.get(id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            logger.info(f"Deleted {self.model.__tablename__} with id={id}")
            return True
        return False

    def exists(self, id: int) -> bool:
        """Check if entity exists."""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None