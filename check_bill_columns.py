from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
SELECT column_name
FROM information_schema.columns
WHERE table_name='bills'
ORDER BY ordinal_position
""")

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()