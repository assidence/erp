#!/usr/bin/env python3
"""
Test customer creation directly using database session
"""
import sys
import os
os.chdir('/home/ubuntu/erp')
sys.path.insert(0, '/home/ubuntu/erp')

from backend.database import SessionLocal
from backend.models.customer import Customer
from datetime import datetime

db = SessionLocal()
try:
    # Create a test customer directly
    customer = Customer(name="Test Customer", created_at=datetime.now(), updated_at=datetime.now())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    print("SUCCESS! Customer created with id:", customer.id)
    print("Name:", customer.name)
    print("Created at:", customer.created_at)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e))
    import traceback
    traceback.print_exc()
finally:
    db.close()