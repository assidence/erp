#!/usr/bin/env python3
import os
import re

frontend_dir = "/home/ubuntu/erp/frontend/src"

# Patterns to search
patterns = [
    (r"from.*['\"]\./pages/Suppliers", "Suppliers import"),
    (r"from.*['\"]\./pages/Parts", "Parts import"),
    (r"from.*['\"]\./pages/MaterialIns", "MaterialIns import"),
    (r"from.*['\"]\./pages/ProductOuts", "ProductOuts import"),
    (r"['\"]\/suppliers['\"]", "suppliers path"),
    (r"['\"]\/parts['\"]", "parts path"),
    (r"['\"]\/material-ins['\"]", "material-ins path"),
    (r"['\"]\/product-outs['\"]", "product-outs path"),
]

for root, dirs, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith(('.jsx', '.js', '.tsx', '.ts')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern, name in patterns:
                        if re.search(pattern, content):
                            print(f"{name}: {filepath}")
            except:
                pass

print("=== Scan complete ===")