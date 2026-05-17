#!/usr/bin/env python3
import os

# Read App.jsx
with open('/home/ubuntu/erp/frontend/src/App.jsx', 'r') as f:
    content = f.read()

print("=== Current App.jsx content ===")
print(content)
print("\n=== Checking for old imports/paths ===")

old_items = ['Suppliers', 'Parts', 'MaterialIns', 'ProductOuts']
for item in old_items:
    if f"import {item}" in content:
        print(f"FOUND: import {item}")
    if f"'{item.lower()}'" in content or f'"/{item.lower()}"' in content:
        print(f"FOUND: path /{item.lower()}")