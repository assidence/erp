#!/usr/bin/env python3
"""
Migration script for M2M relationship tables.
Creates junction tables and migrates existing data from Foundry/Casting customer_id to new tables.

Usage:
    python -m backend.migrations.migrate_m2m
"""
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from backend.database import engine, SessionLocal
from backend.config import get_logger

logger = get_logger(__name__)


def create_junction_tables():
    """Create new junction tables for M2M relationships."""
    with engine.connect() as conn:
        # Create customer_foundries table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_foundries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                foundry_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (foundry_id) REFERENCES foundries(id),
                UNIQUE(customer_id, foundry_id) CONSTRAINT uq_customer_foundry
            )
        """))
        
        # Create customer_castings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_castings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                casting_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (casting_id) REFERENCES castings(id),
                UNIQUE(customer_id, casting_id) CONSTRAINT uq_customer_casting
            )
        """))
        
        # Create parts table (if not exists)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                part_number VARCHAR(100) NOT NULL,
                name VARCHAR(200) NOT NULL,
                description VARCHAR(500),
                images JSON DEFAULT '[]',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """))
        
        # Create part_castings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS part_castings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                casting_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES parts(id),
                FOREIGN KEY (casting_id) REFERENCES castings(id),
                UNIQUE(part_id, casting_id) CONSTRAINT uq_part_casting
            )
        """))
        
        conn.commit()
        logger.info("Junction tables created successfully")


def migrate_existing_data():
    """Migrate existing customer_id data from Foundry and Casting to junction tables."""
    db = SessionLocal()
    try:
        # Migrate Foundry -> CustomerFoundry
        result = db.execute(text("""
            INSERT OR IGNORE INTO customer_foundries (customer_id, foundry_id)
            SELECT customer_id, id FROM foundries WHERE customer_id IS NOT NULL
        """))
        logger.info(f"Migrated {result.rowcount} Foundry->CustomerFoundry links")
        
        # Migrate Casting -> CustomerCasting
        result = db.execute(text("""
            INSERT OR IGNORE INTO customer_castings (customer_id, casting_id)
            SELECT customer_id, id FROM castings WHERE customer_id IS NOT NULL
        """))
        logger.info(f"Migrated {result.rowcount} Casting->CustomerCasting links")
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error migrating data: {e}")
        raise
    finally:
        db.close()


def drop_old_foreign_keys():
    """Drop old customer_id columns from Foundry and Casting tables."""
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN directly in older versions
        # We'll use table recreation approach
        try:
            # For Foundry - recreate table without customer_id
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS foundries_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    contact_person VARCHAR(100),
                    phone VARCHAR(50),
                    address VARCHAR(500),
                    images JSON DEFAULT '[]',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                INSERT INTO foundries_new (id, name, contact_person, phone, address, images, created_at, updated_at)
                SELECT id, name, contact_person, phone, address, images, created_at, updated_at FROM foundries
            """))
            conn.execute(text("DROP TABLE IF EXISTS foundries"))
            conn.execute(text("ALTER TABLE foundries_new RENAME TO foundries"))
            
            logger.info("Foundry table updated - customer_id column removed")
        except Exception as e:
            logger.warning(f"Could not modify foundries table: {e}")
        
        try:
            # For Casting - recreate table without customer_id
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS castings_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_number VARCHAR(100) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description VARCHAR(500),
                    images JSON DEFAULT '[]',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                INSERT INTO castings_new (id, part_number, name, description, images, created_at, updated_at)
                SELECT id, part_number, name, description, images, created_at, updated_at FROM castings
            """))
            conn.execute(text("DROP TABLE IF EXISTS castings"))
            conn.execute(text("ALTER TABLE castings_new RENAME TO castings"))
            
            logger.info("Casting table updated - customer_id column removed")
        except Exception as e:
            logger.warning(f"Could not modify castings table: {e}")
        
        conn.commit()


def run_migration():
    """Run full migration."""
    logger.info("Starting M2M migration...")
    
    logger.info("Step 1: Creating junction tables...")
    create_junction_tables()
    
    logger.info("Step 2: Migrating existing data...")
    migrate_existing_data()
    
    logger.info("Step 3: Cleaning up old foreign keys...")
    drop_old_foreign_keys()
    
    logger.info("M2M migration completed successfully!")


if __name__ == "__main__":
    run_migration()