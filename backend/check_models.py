import sys
import os
os.chdir('/home/ubuntu/erp')
sys.path.insert(0, '/home/ubuntu/erp')

# Clear all backend modules to force reimport
for mod in list(sys.modules.keys()):
    if 'backend' in mod or 'main' in mod:
        del sys.modules[mod]

try:
    from backend.models import (Customer, Supplier, Part, MaterialIn, ProductOut, 
                                ProductionPlan, PaymentPlan, QualityIssue)
    print('All models imported successfully')
    print('Customer relationships:', list(Customer.__mapper__.relationships.keys()))
except Exception as e:
    print('Error:', type(e).__name__, str(e))
    import traceback
    traceback.print_exc()