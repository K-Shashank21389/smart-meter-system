import sqlite3

conn = sqlite3.connect("electricity.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS otp_store(
    meter_no TEXT,
    otp TEXT,
    created_at TEXT
)
""")

conn.commit()
conn.close()

print("OTP Table Created Successfully")