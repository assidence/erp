import sys
sys.path.insert(0, '/home/ubuntu/erp')

import sqlite3
conn = sqlite3.connect('/home/ubuntu/erp/erp.db')
cursor = conn.cursor()

# Check raw foundry data
print("Raw foundries data:")
rows = cursor.execute("SELECT * FROM foundries").fetchall()
if rows:
    cursor.execute("PRAGMA table_info(foundries)")
    cols = [row[1] for row in cursor.fetchall()]
    print(f"Columns: {cols}")
    for r in rows:
        print(f"  {dict(zip(cols, r))}")

# Check if there's customer data that could be used for migration
print("\n\nCustomers:")
cursor.execute("PRAGMA table_info(customers)")
cust_cols = [row[1] for row in cursor.fetchall()]
print(f"Columns: {cust_cols}")
rows = cursor.execute("SELECT * FROM customers").fetchall()
for r in rows:
    print(f"  {dict(zip(cust_cols, r))}")

conn.close()