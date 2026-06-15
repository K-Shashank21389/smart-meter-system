from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
SELECT meter_no, mobile
FROM consumer
""")

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()