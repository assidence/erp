from fastapi.testclient import TestClient
import sys
import os
os.chdir('/home/ubuntu/erp')
sys.path.insert(0, '/home/ubuntu/erp')
from main import app

client = TestClient(app)
r = client.post('/api/customers/', json={'name':'Test'})
print('Status:', r.status_code)
print('Body:', r.text)