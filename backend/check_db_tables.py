import sqlite3
c = sqlite3.connect('/home/ubuntu/erp/backend/erp.db').cursor()
t = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print([r[0] for r in t])