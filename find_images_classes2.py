"""List all classes with images field"""
import sys
sys.path.insert(0, '/home/ubuntu/erp')

# Read the file directly
with open('/home/ubuntu/erp/backend/models/all_models.py', 'r') as f:
    content = f.read()

# Find all class definitions
import re
classes = re.findall(r'class (\w+)\(TimestampMixin', content)

# For each class, check if it has images field
print("=" * 50)
print("Classes in all_models.py:")
print("=" * 50)
for cls in classes:
    pattern = rf'class {cls}.*?images = Column\(JSON'
    if re.search(pattern, content, re.DOTALL):
        print(f"  {cls}: images field PRESENT")
    else:
        print(f"  {cls}: NO images field")