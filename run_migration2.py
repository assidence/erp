import sys
sys.path.insert(0, '/home/ubuntu/erp')
os.chdir('/home/ubuntu/erp')

# Set environment to run from ERP root
os.environ['PYTHONPATH'] = '/home/ubuntu/erp'

import os
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Import database config directly
from backend.database import Base, engine, SessionLocal

def create_tables():
    print("[Step 1] Creating association tables...")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_foundries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                foundry_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (foundry_id) REFERENCES foundries(id) ON DELETE CASCADE,
                UNIQUE(customer_id, foundry_id)
            )
        """))
        print("  - customer_foundries OK")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_castings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                casting_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (casting_id) REFERENCES castings(id) ON DELETE CASCADE,
                UNIQUE(customer_id, casting_id)
            )
        """))
        print("  - customer_castings OK")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS part_castings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                casting_id INTEGER NOT NULL,
                quantity NUMERIC(10, 3) DEFAULT 1,
                notes VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE,
                FOREIGN KEY (casting_id) REFERENCES castings(id) ON DELETE CASCADE,
                UNIQUE(part_id, casting_id)
            )
        """))
        print("  - part_castings OK")
        
        conn.commit()

if __name__ == "__main__":
    create_tables()
    print("\nTable creation successful!")
    
    # Verify tables exist
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print("Tables in database:", tables)