"""Verify images column exists in tables"""
import sys
sys.path.insert(0, '/home/ubuntu/erp')

from backend.database import engine
from sqlalchemy import inspect

def verify():
    inspector = inspect(engine)
    tables = ['material_ins', 'product_outs', 'production_plans']
    
    for table in tables:
        columns = [c['name'] for c in inspector.get_columns(table)]
        has_images = 'images' in columns
        status = "✓" if has_images else "✗"
        print(f"{status} {table}: images={'YES' if has_images else 'NO'}")

if __name__ == "__main__":
    verify()