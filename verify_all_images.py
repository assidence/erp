"""Verify images fields in all models and schemas"""
import sys
sys.path.insert(0, '/home/ubuntu/erp')

from backend.database import engine
from sqlalchemy import inspect

def verify():
    inspector = inspect(engine)
    
    # Models and their tables
    models = [
        ('Casting', 'castings'),
        ('CastingIn', 'casting_ins'),
        ('WorkpieceOut', 'workpiece_outs'),
        ('ProductionPlan', 'production_plans'),
    ]
    
    print("=" * 60)
    print("MODEL & SCHEMA VERIFICATION")
    print("=" * 60)
    
    for model_name, table_name in models:
        print(f"\n### {model_name} ({table_name})")
        
        # Check model
        try:
            from backend.models.all_models import locals()[model_name]
            model = locals()[model_name]
            columns = [c.name for c in model.__table__.columns]
            has_images_model = 'images' in columns
            print(f"  Model: {'✓' if has_images_model else '✗'} images field {'YES' if has_images_model else 'MISSING'}")
        except Exception as e:
            print(f"  Model: ✗ Error - {e}")
        
        # Check database table
        try:
            table_columns = [c['name'] for c in inspector.get_columns(table_name)]
            has_images_db = 'images' in table_columns
            print(f"  Database: {'✓' if has_images_db else '✗'} images column {'EXISTS' if has_images_db else 'MISSING'}")
            if has_images_db:
                col_info = [c for c in inspector.get_columns(table_name) if c['name'] == 'images'][0]
                print(f"    Type: {col_info['type']}, Default: {col_info.get('default', 'None')}")
        except Exception as e:
            print(f"  Database: ✗ Error - {e}")
        
        # Check schema
        try:
            schema_name = model_name.lower() if model_name != 'ProductionPlan' else 'production_plan'
            if model_name == 'CastingIn':
                schema_name = 'casting_in'
            elif model_name == 'WorkpieceOut':
                schema_name = 'workpiece_out'
            
            module = __import__(f'backend.schemas.{schema_name}', fromlist=[f'{model_name}Base'])
            schema_class = getattr(module, f'{model_name}Base')
            schema_fields = schema_class.model_fields
            has_images_schema = 'images' in schema_fields
            print(f"  Schema: {'✓' if has_images_schema else '✗'} images field {'YES' if has_images_schema else 'MISSING'}")
        except Exception as e:
            print(f"  Schema: ✗ Error - {e}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    verify()