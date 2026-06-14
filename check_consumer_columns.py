# check_consumer_columns.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT column_name
FROM information_schema.columns
WHERE table_name='consumer'
""")

print(cursor.fetchall())

conn.close()