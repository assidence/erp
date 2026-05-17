#!/usr/bin/env python3
import re

with open('/home/ubuntu/erp/frontend/src/App.jsx') as f:
    content = f.read()

print("=== App.jsx Verification ===")

# Check imports
imports = re.findall(r'import\s+(\w+)\s+from', content)
print('Imports:', imports)

# Check routes
routes = re.findall(r"path='(/[^']+)'", content)
print('Routes:', routes)

# Check for old paths
old_paths = ['/suppliers', '/parts', '/material-ins', '/product-outs']
for old in old_paths:
    if old in content:
        print(f'ISSUE: Found old path {old}')
    else:
        print(f'OK: {old} not found')

# Check Layout.jsx
print("\n=== Layout.jsx Verification ===")
with open('/home/ubuntu/erp/frontend/src/components/Layout.jsx') as f:
    layout_content = f.read()

for old in old_paths:
    if old in layout_content:
        print(f'ISSUE: Found old path {old}')
    else:
        print(f'OK: {old} not found')