from fastapi.testclient import TestClient
import sys
import os
os.chdir('/home/ubuntu/erp')
sys.path.insert(0, '/home/ubuntu/erp')

# Force reimport by clearing cache
for mod in list(sys.modules.keys()):
    if mod.startswith('backend'):
        del sys.modules[mod]

from main import app

client = TestClient(app, raise_server_exceptions=False)
r = client.post('/api/customers/', json={'name':'Test'})
print('Status:', r.status_code)
print('Body:', r.text)

# Also try GET to confirm server works
r2 = client.get('/api/customers/')
print('GET Status:', r2.status_code)
print('GET Body:', r2.text[:200])