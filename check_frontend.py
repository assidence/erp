import re

# Check App.jsx
with open('/home/ubuntu/erp/frontend/src/App.jsx', 'r') as f:
    app = f.read()

# Check Layout.jsx
with open('/home/ubuntu/erp/frontend/src/components/Layout.jsx', 'r') as f:
    layout = f.read()

print("=== App.jsx imports ===")
foundries = re.findall(r"Foundries", app)
castings = re.findall(r"Castings", app)
castingins = re.findall(r"CastingIns", app)
workpieceouts = re.findall(r"WorkpieceOuts", app)
suppliers = re.findall(r"Suppliers", app)
parts = re.findall(r"Parts", app)
print(f"Foundries: {len(foundries)}, Castings: {len(castings)}, CastingIns: {len(castingins)}, WorkpieceOuts: {len(workpieceouts)}")
print(f"Suppliers: {len(suppliers)}, Parts: {len(parts)}")

print("\n=== App.jsx routes ===")
routes = re.findall(r"path=['\"]([^'\"]+)['\"]", app)
for r in routes:
    print(r)

print("\n=== Layout.jsx paths ===")
paths = re.findall(r"path=['\"]([^'\"]+)['\"]", layout)
for p in paths:
    print(p)