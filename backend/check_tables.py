#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ubuntu/erp/backend')

from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('Current tables:', tables)

# Check for junction tables
junction_tables = [t for t in tables if 'customer_' in t or '_casting' in t]
print('Junction tables:', junction_tables)
