import sys
import os
# Go up one level so backend becomes a package
os.chdir('/home/ubuntu/erp')
sys.path.insert(0, '/home/ubuntu/erp')
from backend.database import get_db
from backend.models.customer import Customer

db_gen = get_db()
db = next(db_gen)
try:
    count = db.query(Customer).count()
    print('Customer count:', count)
    print('Customer columns:', [c.name for c in Customer.__table__.columns])
finally:
    pass