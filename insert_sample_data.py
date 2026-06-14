from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO consumer(
    meter_no,
    name,
    mobile,
    email,
    previous_reading
)
VALUES(
    '240069381738',
    'Shashank',
    '9391179191',
    'YOUR_EMAIL@gmail.com',
    1000
)
ON CONFLICT (meter_no)
DO NOTHING
""")

conn.commit()
conn.close()

print("Consumer Added")