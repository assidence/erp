"""Verify images fields in models directly"""
import sys
sys.path.insert(0, '/home/ubuntu/erp')

from backend.database import engine, Base
from sqlalchemy import inspect, MetaData, Table

def verify():
    inspector = inspect(engine)
    
    # Tables
    tables = ['castings', 'casting_ins', 'workpiece_outs', 'production_plans']
    
    print("=" * 60)
    print("MODEL IMAGES FIELD VERIFICATION")
    print("=" * 60)
    
    all_ok = True
    for table_name in tables:
        print(f"\n{table_name}:")
        
        # Check database table
        try:
            table_columns = [c['name'] for c in inspector.get_columns(table_name)]
            has_images = 'images' in table_columns
            status = "OK" if has_images else "MISSING"
            print(f"  Database: {status}")
            if not has_images:
                all_ok = False
        except Exception as e:
            print(f"  Database: ERROR - {e}")
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("ALL IMAGES FIELDS VERIFIED SUCCESSFULLY")
    else:
        print("WARNING: Some images fields are missing")
    print("=" * 60)

if __name__ == "__main__":
    verify()