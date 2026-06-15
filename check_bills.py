from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
SELECT *
FROM bills
""")

rows = cur.fetchall()

print("TOTAL ROWS =", len(rows))

for row in rows:
    print(row)

conn.close()