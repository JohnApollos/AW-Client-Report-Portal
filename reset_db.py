import sqlite3
import os

DB_PATH = os.environ.get("RAILWAY_DATABASE_PATH", "database.sqlite")
try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS reports")
    conn.execute("DROP TABLE IF EXISTS accounts")
    conn.execute("DROP TABLE IF EXISTS clients")
    conn.commit()
    print("Dropped tables.")
except Exception as e:
    print(e)
