import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="smart_meter",
    user="postgres",
    password="Bachi@21389"
)

print("Connected Successfully")

conn.close()