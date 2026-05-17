"""List all classes with images field"""
import re

with open(r'\\wsl$\Ubuntu\home\ubuntu\erp\backend\models\all_models.py', 'r') as f:
    content = f.read()

# Find all class definitions
classes = re.findall(r'class (\w+)\(TimestampMixin', content)

# For each class, check if it has images field
print("Classes with images field:")
for cls in classes:
    pattern = rf'class {cls}.*?images = Column\(JSON'
    if re.search(pattern, content, re.DOTALL):
        print(f"  - {cls}: images field present")
    else:
        print(f"  - {cls}: NO images field")