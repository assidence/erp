import sys
sys.path.insert(0, '/home/ubuntu/erp')

import sqlite3
conn = sqlite3.connect('/home/ubuntu/erp/erp.db')
cursor = conn.cursor()

# Check foundry columns
cursor.execute("PRAGMA table_info(foundries)")
foundry_cols = [row[1] for row in cursor.fetchall()]
print("Foundries columns:", foundry_cols)

# Check casting columns
cursor.execute("PRAGMA table_info(castings)")
casting_cols = [row[1] for row in cursor.fetchall()]
print("Castings columns:", casting_cols)

# Check customer_foundries columns
cursor.execute("PRAGMA table_info(customer_foundries)")
cf_cols = [row[1] for row in cursor.fetchall()]
print("customer_foundries columns:", cf_cols)

# Check customer_castings columns
cursor.execute("PRAGMA table_info(customer_castings)")
cc_cols = [row[1] for row in cursor.fetchall()]
print("customer_castings columns:", cc_cols)

conn.close()