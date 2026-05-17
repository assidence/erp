"""Migration script to add images JSON column to existing tables"""
import sys
sys.path.insert(0, '/home/ubuntu/erp')

from backend.database import engine
from sqlalchemy import inspect, text

def migrate():
    inspector = inspect(engine)
    
    # Tables to add images column
    tables = ['material_ins', 'product_outs', 'production_plans']
    
    with engine.connect() as conn:
        for table in tables:
            # Check if column exists
            columns = [c['name'] for c in inspector.get_columns(table)]
            
            if 'images' not in columns:
                # Add images column
                try:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN images TEXT DEFAULT '[]'"))
                    conn.commit()
                    print(f"Added images column to {table}")
                except Exception as e:
                    print(f"Error adding images to {table}: {e}")
            else:
                print(f"images column already exists in {table}")
    
    # Verify changes
    print("\nVerifying tables:")
    for table in tables:
        columns = [c['name'] for c in inspector.get_columns(table)]
        print(f"{table}: {columns}")

if __name__ == "__main__":
    migrate()