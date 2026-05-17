import sys
sys.path.insert(0, '/home/ubuntu/erp')

# Delete existing database
import os
db_path = '/home/ubuntu/erp/backend/erp.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted: {db_path}")

# Initialize new database
from backend.database import init_db, engine
from backend.models import *
from sqlalchemy import inspect

init_db()
print("Database initialized")

# Verify tables
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables: {tables}")

# Check customers table structure
if 'customers' in tables:
    columns = [c['name'] for c in inspector.get_columns('customers')]
    print(f"Customers columns: {columns}")
