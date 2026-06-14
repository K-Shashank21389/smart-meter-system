from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS consumer (
    meter_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    meter_no VARCHAR(20),
    bill_date DATE,
    units INTEGER,
    bill_amount NUMERIC,
    status VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usage_history (
    id SERIAL PRIMARY KEY,
    meter_no VARCHAR(20),
    reading_date DATE,
    units INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS otp_store (
    meter_no VARCHAR(20),
    otp VARCHAR(10),
    created_at TIMESTAMP
)
""")

conn.commit()
conn.close()

print("All tables created successfully")