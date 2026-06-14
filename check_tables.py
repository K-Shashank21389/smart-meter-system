# check_tables.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
""")

print(cursor.fetchall())

conn.close()