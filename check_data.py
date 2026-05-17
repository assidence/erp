import sys
sys.path.insert(0, '/home/ubuntu/erp')

import sqlite3
conn = sqlite3.connect('/home/ubuntu/erp/erp.db')
cursor = conn.cursor()

# Count records in each table
tables = ['customers', 'foundries', 'castings', 'parts', 'customer_foundries', 'customer_castings', 'part_castings']
for t in tables:
    try:
        count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t}: {count} rows")
    except Exception as e:
        print(f"{t}: ERROR - {e}")

# Check if there's any relationship data
print("\n--- Sample data ---")
print("\nCustomers:")
rows = cursor.execute("SELECT id, name FROM customers LIMIT 3").fetchall()
for r in rows:
    print(f"  {r}")

print("\nFoundries:")
rows = cursor.execute("SELECT id, name FROM foundries LIMIT 3").fetchall()
for r in rows:
    print(f"  {r}")

print("\nCastings:")
rows = cursor.execute("SELECT id, name FROM castings LIMIT 3").fetchall()
for r in rows:
    print(f"  {r}")

conn.close()