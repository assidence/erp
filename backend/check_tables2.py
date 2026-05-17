import sqlite3
c = sqlite3.connect('/home/ubuntu/erp/backend/erp.db')
cursor = c.cursor()
# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])
# Check file info
import os
print("DB file size:", os.path.getsize('/home/ubuntu/erp/backend/erp.db'), "bytes")
c.close()