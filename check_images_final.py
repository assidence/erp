"""Verify images fields in all models"""
import sys
sys.path.insert(0, '/home/ubuntu/erp')

from backend.database import engine
from sqlalchemy import inspect
from backend.models.all_models import Casting, CastingIn, WorkpieceOut, ProductionPlan

def verify():
    inspector = inspect(engine)
    
    models = [
        ('Casting', 'castings', Casting),
        ('CastingIn', 'casting_ins', CastingIn),
        ('WorkpieceOut', 'workpiece_outs', WorkpieceOut),
        ('ProductionPlan', 'production_plans', ProductionPlan),
    ]
    
    print("=" * 60)
    print("MODEL IMAGES FIELD VERIFICATION")
    print("=" * 60)
    
    all_ok = True
    for model_name, table_name, model_cls in models:
        print(f"\n{model_name} ({table_name}):")
        
        # Check model columns
        columns = [c.name for c in model_cls.__table__.columns]
        has_images = 'images' in columns
        status = "OK" if has_images else "MISSING"
        print(f"  Model: {status}")
        if not has_images:
            all_ok = False
        
        # Check database table
        table_columns = [c['name'] for c in inspector.get_columns(table_name)]
        has_images_db = 'images' in table_columns
        status = "OK" if has_images_db else "MISSING"
        print(f"  Database: {status}")
        if not has_images_db:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("ALL IMAGES FIELDS VERIFIED SUCCESSFULLY")
    else:
        print("WARNING: Some images fields are missing")
    print("=" * 60)

if __name__ == "__main__":
    verify()