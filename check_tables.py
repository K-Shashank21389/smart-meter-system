# check_mobile.py

from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT meter_no,mobile
FROM consumer
""")

print(cursor.fetchall())

conn.close()